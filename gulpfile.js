/*
* gulpfile.js
* Author: Rushy Panchal
* Date: April 4th, 2017
* Description: Gulp task configuration.
*/

var fs = require('fs'),
	path = require('path'),
	exec = require('child_process').exec,
	os = require('os');

var gulp = require('gulp'),
	source = require('vinyl-source-stream'),
	browserify = require('browserify'),
	babelify = require('babelify'),
	Promise = require('promise'),
	_  = require('lodash');

/* Load configuration from environment variables and argv. */
var ENVIRONMENT = process.env.ENV || 'development',
	DEBUG = (ENVIRONMENT == 'development' || process.env.DEBUG),
	ARGV = require('minimist')(process.argv.slice(2)),
	CONFIG = {'shared': 'core/static/core/js'};

/* Promise-based equivalents of fs functions. */
var fs_lstat = Promise.denodeify(fs.lstat),
	fs_readdir = Promise.denodeify(fs.readdir);

function get_dependencies() {
	/* Get the list of dependencies for the current project. */
	var e = require('./package.json');
	return Object.keys(e.dependencies);
	}

function sync_load_search_paths() {
	/* Load the search paths for all JSX files. */
	var search_paths = new Array(),
		dirs = fs.readdirSync('.');

	/* Add any app paths that have the form of {app}/static/react/{app}/
	to the search path for require(). */
	dirs.forEach(function(dir) {
		var full_path = path.join('.', dir),
			app_react_path = path.join('.', dir, 'static', 'react');
		if (fs.lstatSync(full_path).isDirectory() &&
			fs.existsSync(path.join(app_react_path, dir))) {
			search_paths.push(app_react_path);
			}
		});

	return search_paths;
	}

var SEARCH_PATHS = sync_load_search_paths(),
	DEPENDENCIES = get_dependencies(),
	CACHE = new Object();

function make_bundler(config) {
	/* Make a Browserify bundler given the required settings. */
	config = _.merge({
		bundle_name: 'bundle.js', /* bundle name to output to */
		/* path to output bundle to */
		bundle_path: '.',
		is_external: false, /* whether or not the bundle is of external packages */
		entries: new Array(), /* entry points into the bundle */
		dependencies: DEPENDENCIES, /* dependencies for the bundle */
		}, config);

	var bundler = browserify({
		entries: config.entries,
		debug: DEBUG,
		cache: CACHE,
		fullPaths: true,
		paths: SEARCH_PATHS,
		}).transform(babelify, {
			presets: ['es2015', 'react'],
			plugins: ['transform-class-properties'],
			});
	
	bundler.on('dep', function(dep) {
		CACHE[dep.id] = dep;
		});

	if (config.is_external) bundler.require(config.dependencies);
	else bundler.external(config.dependencies);

	if (DEBUG) {
		if (config.is_external) {
			console.log('Browserify external dependencies:',
				config.dependencies.join(', '), '->',
				path.join(config.bundle_path, config.bundle_name));
			}
		else {
			console.log('Browserify:', config.entries.join(', '), '->',
				path.join(config.bundle_path, config.bundle_name));
			}
		}

	return bundler;
	}

function bundle_jsx(config) {
	/* Use bundler to bundle up the JSX file after running the babelify
	transformations. */
	var bundler = make_bundler(config);

	return new Promise(function(resolve, reject) {
		bundler.bundle()
			.pipe(source(config.bundle_name))
			.pipe(gulp.dest(config.bundle_path))
			.on('error', reject)
			.on('end', resolve);
		});
	}

gulp.task('collect', function() {
	/* Run the Django static file collection. */
	var cmd = 'python manage.py collectstatic --no-input -i *.jsx';
	return new Promise(function(resolve, reject) {
		exec(cmd, function(err, stdout, stderr) {
			if (DEBUG) {
				console.log(stdout);
				console.log(stderr);
				}

			if (DEBUG && err) {
				console.log(err);
				process.exit(1);
				}

			resolve();
			});
		});
	});

gulp.task('external', function() {
	/* Bundle the external dependencies. */
	return bundle_jsx({
		bundle_name: 'external.js',
		bundle_path: path.join('.', CONFIG['shared']),
		is_external: true,
		});
	});

gulp.task('bundle', function() {
	/* Bundle the primary React code. Also runs the transformers
	required.
	A sole application can be given using the --app or -a parameter. */
	var app = ARGV.app || ARGV.a;

	if (app) var bundle_apps = [app];
	else {
		process.stderr.write('Usage: gulp bundle -a|-app {app}').
		process.exit(1);
		}

	var promises = bundle_apps.map(function(app) {
		var entry_dir = path.join('.', app, 'static', 'react', app),
			bundle_path = path.join('.', app, 'static', app, 'js', 'bundle'),
			entries = new Array();

		if (fs.existsSync(entry_dir) && fs.lstatSync(entry_dir).isDirectory()) {
			entries = fs.readdirSync(entry_dir);
			}

		var app_promises = entries.map(function(entry) {
			var full_path = path.join(entry_dir, entry);
			if (fs.lstatSync(full_path).isFile()) {
				return bundle_jsx({
					bundle_name: entry.replace('.jsx', '.js'),
					bundle_path: bundle_path,
					entries: [full_path],
					});
				}
			});

		return Promise.all(app_promises);
		});

	return Promise.all(promises);
	});


/* Run tasks in parallel, where possible.
 * If the machine has less than 1GB of memory, run all tasks in series
 * instead of parallel. For specific tasks, this will lead to faster
 * execution because of lower memory usage – less swap is used, and so
 * fewer memory movements (from swap to memory or vice versa) are needed. */
var parallel = (os.totalmem() >= 1e9) ? gulp.parallel: gulp.series;

/* Task aliases. */
gulp.task('default', gulp.series('bundle'));

/* Task compositions. */
gulp.task('all', parallel('bundle', 'external'));
gulp.task('production', gulp.series('all', 'collect'));
