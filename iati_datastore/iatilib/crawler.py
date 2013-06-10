import datetime
import logging
import traceback

import sqlalchemy as sa
import requests
import ckanapi
from dateutil.parser import parse as date_parser
from .queue import get_queue
from werkzeug.http import http_date

from iatilib import db, parse
from iatilib.model import Dataset, Resource, Activity, Log, DeletedActivity

log = logging.getLogger("crawler")


CKAN_WEB_BASE = 'http://iatiregistry.org/dataset/%s'
CKAN_API = 'http://iatiregistry.org'

registry = ckanapi.RemoteCKAN(CKAN_API)

class CouldNotFetchPackageList(Exception):
    pass

def fetch_dataset_list():
    existing_datasets = Dataset.query.all()
    existing_ds_names = set(ds.name for ds in existing_datasets)
    package_list = registry.action.package_list()

    if package_list.get('success', False):
        incoming_ds_names = set(package_list['result'])
        
        new_datasets = [Dataset(name=n) for n
                        in incoming_ds_names - existing_ds_names]
        all_datasets = existing_datasets + new_datasets
        for dataset in all_datasets:
            dataset.last_seen = datetime.datetime.utcnow()
        db.session.add_all(all_datasets)
        db.session.commit()

        deleted_ds_names = existing_ds_names - incoming_ds_names
        if deleted_ds_names:
            delete_datasets(deleted_ds_names)
            all_datasets = Dataset.query.all()

        return all_datasets
    else:
        raise CouldNotFetchPackageList()


def delete_datasets(datasets):
    deleted_datasets = db.session.query(Dataset).filter(Dataset.name.in_(datasets))

    activities_to_delete = db.session.query(Activity).\
                                filter(Activity.resource_url==Resource.url).\
                                filter(Resource.dataset_id.in_(datasets))

                                            
    now = datetime.datetime.now()
    deleted_activities = [ DeletedActivity(
                            iati_identifier=a.iati_identifier,
                            deletion_date=now
                           ) 
                           for a in activities_to_delete ]
    db.session.add_all(deleted_activities)
    db.session.commit()
    deleted = deleted_datasets.delete(synchronize_session='fetch')
    log.info("Deleted {0} datasets".format(deleted))
    return deleted


def fetch_dataset_metadata(dataset):
    ds_reg = registry.action.package_show_rest(id=dataset.name)
    if ds_reg.get('success', False):
        ds_entity = ds_reg['result']
        dataset.last_modified = date_parser(ds_entity.get('metadata_modified', ""))
        new_urls = [resource['url'] for resource
                    in ds_entity.get('resources', [])
                    if resource['url'] not in dataset.resource_urls]
        dataset.resource_urls.extend(new_urls)
        db.session.add(dataset)
        return dataset
    else:
        raise CouldNotFetchPackageList()


def fetch_resource(resource):
    headers = {}
    if resource.last_succ:
        headers['If-Modified-Since'] = http_date(resource.last_succ)
    if resource.etag:
        headers["If-None-Match"] = resource.etag.encode('ascii')
    resp = requests.get(resource.url, headers=headers)
    resource.last_status_code = resp.status_code
    resource.last_fetch = datetime.datetime.utcnow()
    if resp.status_code == 200:
        resource.document = resp.content
        if "etag" in resp.headers:
            resource.etag = resp.headers.get('etag').decode('ascii')
        else:
            resource.etag = None
        resource.last_succ = datetime.datetime.utcnow()
        resource.last_parsed = None
        resource.last_parse_error = None
    if resp.status_code == 304:
        resource.last_succ = datetime.datetime.utcnow()
    db.session.add(resource)
    return resource


def parse_resource(resource):
    db.session.add(resource)
    current = Activity.query.filter_by(resource_url=resource.url)
    current_identifiers = set([ i.iati_identifier for i in current.all() ])

    Activity.query.filter_by(resource_url=resource.url).delete()
    resource.activities = list(parse.document(resource.document, resource))

    #add any identifiers that are no longer present to deleted_activity table
    new_identifiers = set([ i.iati_identifier for i in resource.activities ])
    diff = current_identifiers - new_identifiers 
    now = datetime.datetime.now()
    deleted = [ 
            DeletedActivity(iati_identifier=deleted_activity, deletion_date=now)
            for deleted_activity in diff ]
    if deleted:
        db.session.add_all(deleted)

    #remove any new identifiers from the deleted_activity table
    db.session.query(DeletedActivity)\
            .filter(DeletedActivity.iati_identifier.in_(new_identifiers))\
            .delete(synchronize_session="fetch")

    log.info(
        "Parsed %d activities from %s",
        len(resource.activities),
        resource.url)
    resource.last_parsed = datetime.datetime.utcnow()
    return resource

def update_activities(resource_url):
    resource = Resource.query.get(resource_url)
    try:
        parse_resource(resource)
        # if this resource duplicates any activities from other resources
        # then remove them.
        dup_activity = Activity.query.filter(
            Activity.iati_identifier.in_(
                a.iati_identifier for a in resource.activities
            )
        )
        for db_activity in dup_activity:
            res_activity = next(
                a for a in resource.activities
                if a.iati_identifier == db_activity.iati_identifier
            )
            resource.activities.remove(res_activity)
            db.session.expunge(res_activity)
        log.info("Removed %d duplicate activities", dup_activity.count())
        db.session.commit()
    except parse.ParserError, exc:
        db.session.rollback()
        resource.last_parse_error = str(exc)
        db.session.add(Log(
            dataset=resource.dataset,
            resource=resource.resource_url,
            logger="xml_parser",
            msg="Failed to parse XML file {0} error was".format(resource_url, exc),
            level="error",
            trace=traceback.format_exc(),
            created_at=datetime.datetime.now()
        ))
        db.session.commit()


def update_resource(resource_url):
    rq = get_queue()
    resource = fetch_resource(Resource.query.get(resource_url))
    db.session.commit()

    if resource.last_status_code == 200:
        rq.enqueue(update_activities, args=(resource.url,), result_ttl=0)


def update_dataset(dataset_name):
    rq = get_queue()
    dataset = Dataset.query.get(dataset_name)
    fetch_dataset_metadata(dataset)
    db.session.commit()
    need_update = [r for r in dataset.resources
                   if not r.last_succ or r.last_succ < dataset.last_modified]
    for resource in need_update:
        rq.enqueue(update_resource, args=(resource.url,), result_ttl=0)


from flask.ext.script import Manager
manager = Manager(usage="Crawl IATI registry")


@manager.command
def dataset_list():
    fetch_dataset_list()
    db.session.commit()


@manager.command
def metadata(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching metadata for %s" % dataset.name
        fetch_dataset_metadata(dataset)
        db.session.commit()


@manager.command
def documents(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching documents for %s" % dataset.name
        for resource in dataset.resources:
            if verbose:
                print "Fetching %s" % resource.url,
            fetch_resource(resource)
            if verbose:
                print resource.last_status_code
            db.session.commit()


def status_line(msg, filt, tot):
    return "{filt_c:4d}/{tot_c:4d} ({pct:6.2%}) {msg}".format(
        filt_c=filt.count(),
        tot_c=tot.count(),
        pct=1.0 * filt.count() / tot.count(),
        msg=msg
    )


@manager.command
def status():
    print "%d jobs on queue" % get_queue().count

    print status_line(
        "datasets have no metadata",
        Dataset.query.filter_by(last_modified=None),
        Dataset.query,
    )

    print status_line(
        "datasets not seen in the last day",
        Dataset.query.filter(Dataset.last_seen <
            (datetime.datetime.utcnow() - datetime.timedelta(days=1))),
        Dataset.query,
    )

    print status_line(
        "resources have had no attempt to fetch",
        Resource.query.outerjoin(Dataset).filter(
            Resource.last_fetch == None),
        Resource.query,
    )

    print status_line(
        "resources not successfully fetched",
        Resource.query.outerjoin(Dataset).filter(
            Resource.last_succ == None),
        Resource.query,
    )

    print status_line(
        "resources not fetched since modification",
        Resource.query.outerjoin(Dataset).filter(
            sa.or_(
                Resource.last_succ == None,
                Resource.last_succ < Dataset.last_modified)),
        Resource.query,
    )

    print status_line(
        "resources not parsed since mod",
        Resource.query.outerjoin(Dataset).filter(
            sa.or_(
                Resource.last_succ == None,
                Resource.last_parsed < Dataset.last_modified)),
        Resource.query,
    )

    print status_line(
        "resources have no activites",
        db.session.query(Resource.url).outerjoin(Activity)
        .group_by(Resource.url)
        .having(sa.func.count(Activity.iati_identifier) == 0),
        Resource.query,
    )

    print
    # out of date activitiy was created < resource last_parsed
    print "{nofetched_c}/{res_c} ({pct:.2%}) activities out of date".format(
        nofetched_c=Activity.query.join(Resource).filter(
            Activity.created < Resource.last_parsed).count(),
        res_c=Activity.query.count(),
        pct=1.0 * Activity.query.join(Resource).filter(
            Activity.created < Resource.last_parsed).count() /
            Activity.query.count()
    )


@manager.command
def enqueue(careful=False):
    rq = get_queue()
    if careful and rq.count > 0:
        print "%d jobs on queue, not adding more" % rq.count
        return

    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)

    unfetched_resources = Resource.query.filter(
        sa.or_(
            Resource.last_fetch == None,
            sa.and_(
                Resource.last_succ == None,
                Resource.last_fetch <= yesterday
            )))
    print "Enqueuing {0:d} unfetched resources".format(
        unfetched_resources.count()
    )
    for resource in unfetched_resources:
        rq.enqueue(
            update_resource,
            args=(resource.url,),
            result_ttl=0)

    ood_resources = Resource.query.filter(sa.or_(
        Resource.last_parsed == None,
        Resource.activities.any(Activity.created < Resource.last_parsed)
    ))

    print "Enqueuing {0:d} resources with out of date activities".format(
        ood_resources.count()
    )
    for resource in ood_resources:
        rq.enqueue(
            update_activities,
            args=(resource.url,),
            result_ttl=0)


@manager.option('--dataset', action="store", type=unicode,
                help="update a single dataset")
@manager.option('--limit', action="store", type=int,
                help="max no of datasets to update")
@manager.option('-v', '--verbose', action="store_true")
def update(verbose=False, limit=None, dataset=None):
    """
    Fetch all datasets from IATI registry; update any that have changed
    """
    rq = get_queue()

    if dataset:
        print "Enqueing {0} for update".format(dataset)
        rq.enqueue(update_dataset, args=(dataset,), result_ttl=0)
        res = Resource.query.filter(Resource.dataset_id==dataset)
        for resource in res:
            rq.enqueue(update_resource, args=(resource.url,), result_ttl=0)
            rq.enqueue(update_activities, args=(resource.url,), result_ttl=0)
    else:
        fetch_dataset_list()
        db.session.commit()

        datasets = Dataset.query
        if limit:
            datasets = datasets.limit(limit)

        print "Enqueing %d datasets for update" % datasets.count()

        for dataset in datasets:
            if verbose:
                print "Enquing %s" % dataset.name
            rq.enqueue(update_dataset, args=(dataset.name,), result_ttl=0)

