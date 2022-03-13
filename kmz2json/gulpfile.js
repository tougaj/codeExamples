const gulp = require('gulp');
const ts = require('gulp-typescript');
var changed = require('gulp-changed');
const replace = require('gulp-replace');
const del = require('del');
const plumber = require('gulp-plumber');

let paths = {
	scripts: {
		src: ['src/js/**/*.ts', 'src/js/**/*.tsx', '!src/**/*.d.ts'],
		dest: 'js',
	},
};

let tsProject = ts.createProject('./tsconfig.json');
function typeScripts() {
	let tsResult = gulp
		.src(paths.scripts.src)
		.pipe(plumber())
		// .pipe(changed('.', { extension: '.js' }))
		.pipe(tsProject());

	return tsResult.js.pipe(gulp.dest(paths.scripts.dest));
}

const sDistDir = './dist';

const clean = () => del([sDistDir]);

function watch() {
	gulp.watch(paths.scripts.src, typeScripts);
}

gulp.task('ts', typeScripts);

gulp.task('build', gulp.series(clean, typeScripts));

let development = gulp.series(typeScripts, watch);
gulp.task('default', development);
