const gulp = require('gulp');
const ts = require('gulp-typescript');

let paths = {
	styles: {
		src: 'src/css/*.sass',
		dest: 'css',
	},
	scripts: {
		src: 'src/js/*.ts',
		dest: 'js',
	},
};

let tsProject = ts.createProject('./tsconfig.json');

function typeScripts() {
	let tsResult = gulp
		.src(paths.scripts.src)
		// .pipe(changed('./js', {extension: '.js'}))
		.pipe(tsProject());

	return tsResult.js.pipe(gulp.dest(paths.scripts.dest));
}

function watch() {
	gulp.watch(paths.scripts.src, typeScripts);
}

gulp.task('ts', typeScripts);

let development = gulp.series(typeScripts, watch);
gulp.task('default', development);
