# COS-333

## Docker
Docker is used to run each component of the project in separate containers.
You can install it [here](https://www.docker.com/community-edition#/download).
Once installed, run the newly installed Docker engine.

To build the containers for the project, run `$ docker-compose build`. Now, you
can run `$ docker-compose up` to run the project (which is accessible by
default at `http://localhost:8000`).

Any changes in the local directory will be synced automatically to the
container. To run a command on the web container, which is where the Django
project runs, run `$ docker-compose run web {command}`. For example, to run
Django's migrations: `$ docker-compose run web python manage.py migrate`.
