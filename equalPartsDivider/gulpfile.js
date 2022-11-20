const gulp = require('gulp');
const changed = require('gulp-changed');
const plumber = require('gulp-plumber');
const ts = require('gulp-typescript');

const paths = {
	server: {
		src: 'src/**/*.ts',
		dest: './dst',
	},
};

function typeScript() {
	const tsProject = ts.createProject('./tsconfig.json');
	const tsResult = gulp
		.src(paths.server.src)
		.pipe(plumber())
		.pipe(changed(paths.server.dest, { extension: '.js' }))
		.pipe(tsProject());

	return tsResult.js.pipe(plumber()).pipe(gulp.dest(paths.server.dest));
}
gulp.task('ts', typeScript);

function watch() {
	gulp.watch(paths.server.src, typeScript);
}

gulp.task('default', gulp.series(typeScript, watch));
