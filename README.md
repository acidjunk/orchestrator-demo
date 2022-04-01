# Orchestrator Demo

This project contains a demo of the Orchestrator.

## Server

This project only works with Python 3.10
This project is not cloneable with windows because some files are invalid for the file system, Use WSL or change to 
linux OS.

If you want to use a virtual environment first create the environment:

```shell
python3 -m venv .venv
source .venv/bin/activate
```

You can install the required libraries with pip. The following command will install all the required
libraries for the project. Check out the different files under requirements to more specifically see
which library is used and for what reason.

```shell
pip install -r ./requirements/all.txt
```

A PostgreSQL user and two databases are required ('orchestrator-demo' is the password used by default). 
Make sure you use Postgres 12 or higher.

```shell
createuser -s -P orchestrator-demo

createdb orchestrator-demo -O orchestrator-demo
createdb orchestrator-demo-test -O orchestrator-demo
```

### ENV file example

This is an example of the environment file to run the FastAPI application in development mode and to be able to use the CLI commands.

Put this in `.env` file in the git root. Populate where needed with your personal information.
For more information about the population values, see [this wiki page](https://wiki.surfnet.nl/display/NWAO/Developer+allocations)

```shell
export HTTP_PORT=8080
export MAIL_PORT=1025
export NSO_ENABLED=True
export OAUTH2_ACTIVE=False
export STACK_LIMIT=""
export SERVER_THREADED=1
export TESTING=False
export DATABASE_URI="postgresql://orchestrator-demo:orchestrator-demo@localhost/orchestrator-demo"
export DATABASE_URI_TEST="postgresql://orchestrator-demo:orchestrator-demo@localhost/orchestrator-demo-test"
export WEBSOCKET_BROADCASTER_URL="redis://localhost:6379"

# Populator config
export POPULATOR_ORGANISATION="<uuid for personal org>"
export POPULATOR_CONTACT_NAME="<name>"
export POPULATOR_CONTACT_EMAIL="<email address>"
export POPULATOR_CONTACT_PHONE="<phone number>" # optional
```

FastAPI detects and loads immediately the `.env` file. If you chose to give a name
to your file eg `filename.env`, then you need to explicitly load it. Do `source <filename.env>`.

### Development Mode

The server is a FastAPI application. The first time that you set up your environment,
you can start the server in development mode without scheduling.

To run in development mode without scheduling, but with threads:

```shell
./bin/server
```

You can also ensure that you loaded the needed env vars and run a hot reloading webserver:

```shell
DATABASE_URI=postgresql://orchestrator-demo:orchestrator-demo@localhost/orchestrator-demo PYTHONPATH=. uvicorn main:app --reload --port 8080
```

If you keep forgetting the commands; don't worry you can also use the `./start.sh` script. It will
load the venv, set ENV vars and start the webserver. By default, it starts a threaded server. If you
want the auto-reload functionality enabled: `./start.sh dev`

### Running fastapi CLI commands

We use [Typer](https://typer.tiangolo.com) for our CLI. Some examples:

show list OF available commands:

```shell
PYTHONPATH=. python main.py --help
PYTHONPATH=. python main.py scheduler
```

### Troubleshooting:

Make sure your virtual environment is activated in the terminal, where you start the back-end!

You can confirm that the back-end is available by:

```shell
    curl localhost:8080/api/products
```

You should receive a json output of products.

- If instead you receive:
  ```
      {
        "detail": "No Authorization token provided",
        "status": 401,
        "title": "Unauthorized",
        "type": "about:blank"
      }
  ```
  Then that means that you did not export the OAUTH2_ACTIVE=False. This should be in your .env file defined,
  thus do `source .env` to load your environment variables.

### Scheduling Mode

If you need to test the schedules use the other binary

```shell
./bin/scheduling
```

The scheduler can also be forced to run just one schedule and quit. This is very useful for development purposes. You can execute it like this:

```shell
./bin/scheduling force validate_node
```

That will run only the `validate_node` schedule and quit when it's done.

## Tests

Unit tests are organized in `test` and use the standard python `unittest` module. Also doctests are supported.

To run all tests (including doctests), use `pytest`:

```shell
pytest
```

To generate coverage reports:

```shell
pytest --cov=surf --cov-report html:htmlcov test
open htmlcov/index.html
```

Note that the user under which the database connection runs (as set in DB_URI environment variable/parameter) should
have CREATEDB rights. This can be accomplished by:

```sql
ALTER USER orchestrator-demo CREATEDB;
```

## Pre-commit hooks

If you want you can install the pre-commit hooks to ease the development process.

```shell
pre-commit install
```

### DB migrations

The database schema is maintained by migrations (see `/migrations` for the
definitions). Pending migrations are automatically applied when starting the
server.

In the orchestrator we have two migration branches that move independently of one another. The data branch which contains
all custom data that we need at SURF and the Schema branch that will be opensourced.

The db module has also been refactored to show the difference between SURF models and generic models. The models are
then re-exported so they remain transparent to the application.

If you are introducing a SURF specific table add the prefix `sn`

### Schema migration

Note: the command assume you loaded your ENV correctly with DB setting.

To create a new schema migration:

```shell
PYTHONPATH=. python main.py db revision --autogenerate -m "New schema" --head=schema@head
```

This opens a new migration in \$PWD/migrations/version/

We use Alembic to make migrations, they use db.py as source to define
the database structure

### General Migration

To create a data migration do the following:

```shell
PYTHONPATH=. python main.py db revision --message "Name of the migration" --head=data@head
```

This will also create a new revision file where normal SQL can be written like so:

```python
conn = op.get_bind()
res = conn.execute("INSERT INTO products VALUES ('x', 'y', 'z')")
```

### Inter migration branch dependencies

It may be necessary to apply a data migration after a schema migration has taken place. In that case generate the schema
migration and then the data migration as specified above.
Then edit the header of the data migration file and change the
depends_on line to reference the `slug` of the schema migration.

The slug or revision id can be found by either looking at the revision in the most recent migration file, or by executing

```bash
PYTHONPATH=. python main.py db heads
```

Below you see the depends_on line.

```python
# revision identifiers, used by Alembic.
revision = "812dd7e3b17e"
down_revision = None
branch_labels = ("data",)
depends_on = "8c66ee7ad04a"  # THIS LINE
```

**DO NOT MAKE SCHEMA MIGRATIONS DEPENDENT ON GENERAL MIGRATIONS**

### Applying migrations

Applying migrations will happen when you start the webserver. If you want to manually apply migrations you can do it ike this:

```shell
PYTHONPATH=. python main.py db upgrade heads
```

When a downgrade has been written use:

```shell
PYTHONPATH=. python main.py db downgrade heads
```

_There is no policy as yet to support downgrades_

### Troubleshooting migrations after merge

Sometimes after a merge you'll get a conflict due to migrations that where added in other branches. Alembic has an easy way to solve this kind of problems.
In the console output you, most likely, will find the two versions that have a conflict.

Run this command to solve the conflict:

```shell
 PYTHONPATH=. python main.py db merge <revision_id> <revision_id>
```

_Don't forget to 'git add' the resulting file, if it fixed the migration problem_

## Docker

Deploys of Workflows are in the form of a Docker image.
Since Workflows depends on the nwa-stdlib it needs an SSH key to clone the git repository
from (internal) Gitlab. This key must be stored in id_rsa prior to building the Docker image.

At runtime a container needs to specify a bunch of environment variables for Workflows to run.
An easy way to specify these (on your development machine) is to put them in .dockerenv and
provide the --env-file parameter to docker run.
