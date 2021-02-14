import os
from os.path import dirname, realpath, join
import codecs
import logging
import datetime as dt
import subprocess

import click
from flask.cli import FlaskGroup, with_appcontext
import requests
from sqlalchemy import not_

from iatilib import parse, codelists, db
from iatilib.frontend.app import create_app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the IATI application."""
    pass


@cli.command()
@with_appcontext
def download_codelists():
    "Download CSV codelists from IATI"
    for major_version in ['1', '2']:
        for name, url in codelists.urls[major_version].items():
            filename = "iati_datastore/iatilib/codelists/%s/%s.csv" % (major_version, name)
            print("Downloading %s.xx %s" % (major_version, name))
            resp = requests.get(url[major_version])
            resp.raise_for_status()
            resp.encoding = "utf-8"
            assert len(resp.text) > 0, "Response is empty"
            with codecs.open(filename, "w", encoding=resp.encoding) as cl:
                cl.write(resp.text)


@cli.command()
@with_appcontext
def cleanup():
    from iatilib.model import Log
    db.session.query(Log).filter(
            Log.created_at < dt.datetime.utcnow() - dt.timedelta(days=5)
    ).filter(not_(Log.logger.in_(
            ['activity_importer', 'failed_activity', 'xml_parser']),
    )).delete('fetch')
    db.session.commit()
    db.engine.dispose()


@cli.command()
def build_docs():
    """Build documentation from source."""
    current_path = dirname(dirname(realpath(__file__)))
    cwd = join(current_path, 'docs_source')
    subprocess.run(['make', 'dirhtml'], cwd=cwd)


@click.option('--deploy-url', 'deploy_url', type=str)
@cli.command()
def build_query_builder(deploy_url=None):
    """Build query builder (front page)."""
    current_path = dirname(dirname(realpath(__file__)))
    cwd = join(current_path, 'query_builder_source')
    subprocess.run(['npm', 'i'], cwd=cwd)

    if deploy_url is not None:
        env = {
            **os.environ,
            "IATI_DATASTORE_DEPLOY_URL": deploy_url,
        }
        subprocess.run(['npm', 'run', 'generate'], cwd=cwd, env=env)
    else:
        subprocess.run(['npm', 'run', 'generate'], cwd=cwd)


@click.option(
        '-x', '--fail-on-xml-errors', "fail_xml")
@click.option(
        '-s', '--fail-on-spec-errors', "fail_spec")
@click.option('-v', '--verbose', "verbose")
@click.argument('filenames', nargs=-1)
@cli.command()
@with_appcontext
def parse_file(filenames, verbose=False, fail_xml=False, fail_spec=False):
    for filename in filenames:
        if verbose:
            print("Parsing", filename)
        try:
            db.session.add_all(parse.document_from_file(filename))
            db.session.commit()
        except parse.ParserError as exc:
            logging.error("Could not parse file %r", filename)
            db.session.rollback()
            if isinstance(exc, parse.XMLError) and fail_xml:
                raise
            if isinstance(exc, parse.SpecError) and fail_spec:
                raise


@cli.command()
@with_appcontext
def drop_database():
    """Drop all database tables."""
    click.confirm('Are you sure?', abort=True)
    db.drop_all()
