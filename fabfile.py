from contextlib import contextmanager

from fabric import task


@contextmanager
def virtualenv(conn):
    with conn.cd('~/iati-datastore'):
        with conn.prefix('source pyenv/bin/activate'):
            yield


@task
def deploy(conn):
    with virtualenv(conn):
        # pull latest copy of code in version control
        conn.run('git pull origin main')
        # install dependencies
        conn.run('pip install -r requirements.txt')
        # run database migrations
        conn.run('iati db upgrade')
        # build the docs
        conn.run('iati build-docs')
        # build the query builder
        conn.run('iati build-query-builder --deploy-url https://datastore.codeforiati.org')
        # stop everything
        conn.run('sudo systemctl stop iati-datastore')
        conn.run('sudo systemctl stop iati-datastore-queue')
        # start everything again
        conn.run('sudo systemctl start iati-datastore')
        conn.run('sudo systemctl start iati-datastore-queue')
