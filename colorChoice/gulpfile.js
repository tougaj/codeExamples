const gulp = require('gulp');
let browserSync = require('browser-sync').create();
const autoprefixer = require('gulp-autoprefixer');
const csslint = require('gulp-csslint');
const sass = require('gulp-sass');
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

function styles() {
	return gulp
		.src(paths.styles.src)
		.pipe(sass().on('error', sass.logError))
		.pipe(
			csslint({
				lookup: false,
				ids: false,
				shorthand: true,
				'order-alphabetical': false,
				'qualified-headings': false,
				'box-model': false,
				'adjoining-classes': false,
				important: false,
			})
		)
		.pipe(csslint.formatter())
		.pipe(autoprefixer({}))
		.pipe(gulp.dest(paths.styles.dest));
	// .pipe(browserSync.reload({stream: true}));
}

let tsProject = ts.createProject('./tsconfig.json');

function typeScripts() {
	let tsResult = gulp
		.src(paths.scripts.src)
		// .pipe(changed('./js', {extension: '.js'}))
		.pipe(tsProject());

	return tsResult.js.pipe(gulp.dest(paths.scripts.dest));
}

function watch() {
	browserSync.init({
		server: true,
		files: ['css/*.css', 'js/*.js', '*.html'],
	});
	gulp.watch(paths.styles.src, styles);
	gulp.watch(paths.scripts.src, typeScripts);
	// gulp.watch('./index.html').on('change', browserSync.reload);
}

gulp.task('sass', styles);
gulp.task('ts', typeScripts);

let development = gulp.series(styles, typeScripts, watch);
gulp.task('default', development);

// gulp.task('default', ['sass'], () => {
// 	// browserSync.init({
// 	// 	// server: {
// 	// 	// 	files: ['./*.css', './*.js', './*.php']
// 	// 	// 	// serveStatic: ['.', './app/css']
// 	// 	// },
// 	// 	// proxy: 'http://localhost/Execute/edr/' // work
// 	// 	// proxy: 'http://localhost:8080/stater/' // home
// 	// 	// serveStatic: ['./*.css', './*.js', './*.php']
// 	// });

// 	gulp.watch(sassSource, ['sass']);
// 	// gulp.watch('./index.php').on('change', browserSync.reload);
// });
