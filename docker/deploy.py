# docker/deploy.py
# CourseGenie
# Author: Rushy Panchal
# Date: March 24th, 2017
# Description: Deploy CourseGenie to DigitalOcean.

import os
import re
import sys
import argparse
import subprocess

__version__ = '0.1'
__description__ = '''
CourseGenie deployment tool.
By default, the DigitalOcean driver is used, with configuration options listed
here: https://docs.docker.com/machine/drivers/digital-ocean/#options.

To pass extra options to docker-machine, use -- {options}. For example,
"python deploy.py -- -f --some-other-option"
'''

stderr = sys.stderr
BASEDIR = '' if os.path.dirname(__file__) else '..'
DEBUG = int(os.environ.get('DEBUG', 0))
DOCKER_MACHINE_ENV = [
	'DOCKER_TLS_VERIFY',
	'DOCKER_HOST',
	'DOCKER_CERT_PATH',
	'DOCKER_MACHINE_NAME'
	]
DEFAULT_COMPOSE_FILE = os.path.join(BASEDIR, 'docker', 'compose',
	'production.yml')

def main():
	parser = argparse.ArgumentParser(version=__version__,
		description=__description__)
	parser.add_argument('-d', '--driver', dest='driver', default='digitalocean',
		help='Driver to use for docker-machine.')
	parser.add_argument('-s', '--size', dest='size', default='512mb',
		help='Size of droplet (default: 512mb).')
	parser.add_argument('-r', '--region', dest='region', default='nyc3',
		help='DigitalOcean region to deploy droplet to (default: nyc3).')
	parser.add_argument('-n', '--name', dest='name', default='coursegenie',
		help='Name of droplet (default: coursegenie).')
	parser.add_argument('-6', '--ipv6', action='store_true', default=True,
		dest='ipv6', help='Enable IPv6 for the droplet (default: True).')
	parser.add_argument('-b', '--backups', action='store_true', default=False,
		dest='backups', help='Enable backups for the droplet (default: False).')
	parser.add_argument('-c', '--cloud-init',
		default=os.path.join(BASEDIR, 'docker', 'digitalocean.sh'),
		dest='cloudinit_file', help='Cloud Init file.')
	parser.add_argument('--disable-cloud-init', action='store_false',
		default=True, dest='cloudinit', help='Disable cloud-init.')
	subparsers = parser.add_subparsers(title='subcommands',
		description='valid subcommands')

	subparsers.add_parser('deploy', help='Deploy project.').set_defaults(
		func=docker_deploy)
	subparsers.add_parser('config', help='Display configuration.').set_defaults(
		func=display_config)
	subparsers.add_parser('migrate', help='Run Django migrations.').set_defaults(
		func=django_migrate)
	(subparsers.add_parser('push', help='Push updates to remote containers')
		.set_defaults(func=machine_push))

	args, remainder = parser.parse_known_args()
	if DEBUG:
		stderr.write('Parsed Arguments: %s\nRemainder: %s\n' % (args, remainder))

	if len(remainder) and remainder[0] != '--': # '--' separator is required
		remainder = []
	else:
		remainder = remainder[1:] # strip out the '--' separator

	if 'COMPOSE_FILE' not in os.environ:
		os.environ['COMPOSE_FILE'] = DEFAULT_COMPOSE_FILE
	if DEBUG:
		stderr.write('Environment:\n %s' % os.environ)

	args.func(args, remainder)

def docker_deploy(args, remainder):
	'''Deploy the project.'''
	# Clear any remaining environment variables that may have persisted from
	# a global run. This ensures that the environment starts out "clean".
	for k in DOCKER_MACHINE_ENV:
		os.environ.pop(k, None)

	machine_create(args, remainder)
	machine_scp(args.name)

	env = get_machine_environment(args.name)
	os.environ.update(env)

	print('Building containers...')
	docker_compose(args.name, 'build')

	print('Starting containers...')
	docker_compose(args.name, 'up', '-d')

	print('Running Django migrations...')
	docker_compose(args.name, 'run', 'web', 'docker/wait-for-it.sh', '-t', '0',
		'--strict', 'db:5432', '--', 'python', 'manage.py', 'migrate')

	print('Running setup code...')
	docker_compose(args.name, 'run', 'web', 'docker/wait-for-it.sh', '-t', '0',
		'--strict', 'db:5432', '--', 'docker/services/init_web.sh')

def display_config(args, remainder):
	'''Display the configuration for the project.'''
	print('Environment: %s' % os.environ)
	print('Docker Configuration:\n')
	print(docker_call(['docker-compose', 'config'], args.name, 'docker-compose',
		t='check_output', destroy_on_error=False))

def django_migrate(args, remainder):
	'''Run Django migrations for project.'''
	try:
		env = get_machine_environment(args.name, destroy_on_error=False)
	except:
		pass
	else:
		os.environ.update(env)

	print('Running Django migrations...')
	docker_compose(args.name, 'run', 'web', 'python', 'manage.py', 'migrate',
		destroy_on_error=False)

def machine_push(args, remainder):
	'''Push code to servers and redeploy containers.'''
	machine_scp(args.name, destroy_on_error=False)
	env = get_machine_environment(args.name)
	os.environ.update(env)

	print('Building containers...')
	docker_compose(args.name, 'build', destroy_on_error=False)

	print('Restarting containers...')
	docker_compose(args.name, 'up', '-d', destroy_on_error=False)

def machine_create(args, remainder):
	'''Create the machine via docker-machine.'''
	commands = [
		'docker-machine', 'create',
		'--driver', args.driver,
		]

	if args.driver == 'digitalocean':
		commands.extend([
			'--digitalocean-size', args.size,
			'--digitalocean-region', args.region,
			])
		if args.ipv6:
			commands.append('--digitalocean-ipv6')
		if args.backups:
			commands.append('--digitalocean-backups')
		if args.cloudinit:
			commands.extend([
				'--digitalocean-userdata',
				args.cloudinit_file
				])
	commands.extend(remainder)
	commands.append(args.name)

	print('Creating machine...')
	docker_call(commands, args.name, t='call', destroy_on_error=args.name)

def get_machine_environment(name, **kwargs):
	'''Get the docker-machine environment for the given machine.'''
	bash_env_re = re.compile(r'^export (?P<name>[A-Z_]+)=("?)(?P<value>.+)\2$')
	output = docker_call([
		'docker-machine', 'env', name,
		'--shell', 'bash', # bash's export syntax is easiest to parse
		], name, **kwargs)

	data = filter(None, map(bash_env_re.match, output.splitlines()))
	return {x.group('name'): x.group('value') for x in data}

def machine_scp(name, *args, **kwargs):
	'''Push the local code to the machine.'''
	app_dir = '/app'

	env_path = os.path.join(BASEDIR, '.env')
	if os.path.exists(env_path):
		env_re = re.compile(r'^(?P<name>[A-Z_]+)="?(?P<value>.+)"?$')
		with open(env_path) as f:
			data = filter(None, map(env_re.match, f.readlines()))
			env_vars = {x.group('name'): x.group('value') for x in data}

		app_dir = env_vars.get('APP_DIR', app_dir)

	commands = [
		'docker-machine', 'scp',
		'-r', '.', '%s:%s' % (name, app_dir),
		]
	print('Uploading code...')
	docker_call(commands, name, *args, t='call', **kwargs)

def docker_compose(name, *args, **kwargs):
	'''Run a command with docker-compose.'''
	commands = ['docker-compose']
	commands.extend(args)
	docker_call(commands, name, cmd='docker-compose', t='call', **kwargs)

def docker_call(commands, name, cmd='docker-machine', t='check_output',
	destroy_on_error=True):
	'''Try calling docker-machine with the provided commands.'''
	if DEBUG:
		stderr.write(' '.join(commands))
		stderr.write('\n')
	if DEBUG == 2:
		return ''

	output = ''
	try:
		kwargs = {}
		if t == 'check_output':
			kwargs['stderr'] = subprocess.STDOUT

		output = getattr(subprocess, t)(commands, **kwargs)
	except subprocess.CalledProcessError as e:
		print('Error %d: %s\n' % (e.returncode, e.output))
		if destroy_on_error:
			docker_abort(name)
	except OSError:
		print(("Command '%s' not found. Get Docker here: " % cmd)
			+ "https://docs.docker.com/engine/installation/#docker-variants")
		if destroy_on_error:
			docker_abort(name)

	return output

def docker_abort(name, exit_code=1):
	'''Abort the setup and undo any changes made.'''
	print('Aborting setup due to error - killing & removing machine.')
	try:
		output = subprocess.check_output([
			'docker-machine', 'ls',
			'--filter', 'name=%s' % name
			])
	except OSError:
		sys.exit(exit_code)

	if name in output:
		try:
			subprocess.call([
				'docker-machine', 'rm',
				'-f', name
				])
		except (subprocess.CalledProcessError, OSError):
			# Not our problem anymore, we put in our 'best effort'.
			print("Unable to remove machine; run 'docker-machine rm -f %s'." % name)

	sys.exit(exit_code)

if __name__ == '__main__':
	main()
