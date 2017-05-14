# CourseGenie

## Docker
Docker is used to run each component of the project in separate containers.
You can install it [here](https://www.docker.com/community-edition#/download).
Once installed, run the newly installed Docker engine.

To build the containers for the project, run `$ docker-compose build`. This
step is only necessary when the infrastructure changes (including adding new
Python/NodeJS requirements).

Now, you can run `$ docker-compose up` to run the project (which is accessible
by default at `http://localhost:8000`). In case any migrations were made to the
database schema (i.e. if you receive a message of the form
`You have {n} unapplied migration(s).` when running `$ docker-compose up`), run
`$ docker-compose exec web python manage.py migrate`.

Any changes in the local directory will be synced automatically to the
container. To run a command on the web container, which is where the Django
project runs, run `$ docker-compose exec web {command}`. For example, to run
Django's migrations: `$ docker-compose exec web python manage.py migrate`.

### run vs. exec

`$ docker-compose run {container} {command}` should be used if you want to run
a command on a container service without having such a container running.
However, note that it will cause a new container to be spawned, which means
that using `run` repeatedly will slow down Docker after a while. To alleviate
this, you can stop containers using `$ docker stop {container_id}$` where the
`container_id` can be found using `$ docker-compose ps`.

On the other hand, `$ docker-compose exec {container} {command}` executes a
command on the running instances of the container. This prevents a new
container from spawning, so Docker will *not* slow down overtime. However, you
need to have a container running. In addition, these changes will not persist
when spawning a new container.
