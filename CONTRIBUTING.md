# CourseGenie

## Docker
Docker is used to run each component of the project in separate containers.
You can install it [here](https://www.docker.com/community-edition#/download).
Once installed, run the newly installed Docker engine.

To build the containers for the project, run `$ docker-compose build`. This
step is only necessary when the infrastructure changes (including adding new
Python requirements).

Now, you can run `$ docker-compose up` to run the project (which is accessible
by default at `http://localhost:8000`). In case any migrations were made to the
database schema (i.e. if you receive a message of the form
`You have {n} unapplied migration(s).` when running `$ docker-compose up`), run
`$ docker-compose run web python manage.py migrate`.

Any changes in the local directory will be synced automatically to the
container. To run a command on the web container, which is where the Django
project runs, run `$ docker-compose run web {command}`. For example, to run
Django's migrations: `$ docker-compose run web python manage.py migrate`.
