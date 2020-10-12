const gulp = require('gulp');
let browserSync = require('browser-sync').create();
const autoprefixer = require('gulp-autoprefixer');
const csslint = require('gulp-csslint');
const sass = require('gulp-sass');
const ts = require('gulp-typescript');
var changed = require('gulp-changed');
const replace = require('gulp-replace');
var cleanCSS = require('gulp-clean-css');
const webpack = require('webpack-stream');
const del = require('del');
const plumber = require('gulp-plumber');

let paths = {
	styles: {
		src: 'src/css/*.sass',
		dest: 'css',
	},
	scripts: {
		src: ['src/js/**/*.ts', 'src/js/**/*.tsx', '!src/**/*.d.ts'],
		dest: 'js',
	},
};

const styles = () =>
	gulp
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
		.pipe(gulp.dest(paths.styles.dest))
		.pipe(browserSync.reload({ stream: true }));

let tsProject = ts.createProject('./tsconfig.json');
function typeScripts() {
	let tsResult = gulp
		.src(paths.scripts.src)
		.pipe(changed('.', { extension: '.js' }))
		.pipe(tsProject());

	return tsResult.js.pipe(gulp.dest(paths.scripts.dest));
}

const sDistDir = './dist';

const clean = () => del([sDistDir]);
const webpackDev = () => runDevWebPack('js/**/*.js', './js/index.js');
const webpackProd = () => runProdWebPack('js/**/*.js', './js/index.js', `${sDistDir}/js`);

function watch() {
	browserSync.init({
		server: true,
		files: ['css/*.css', 'js/*.js', '*.html'],
	});
	gulp.watch(paths.styles.src, styles);
	gulp.watch(paths.scripts.src, gulp.series(typeScripts, webpackDev));
	gulp.watch('./index.html').on('change', browserSync.reload);
}

gulp.task('sass', styles);
gulp.task('ts', typeScripts);
gulp.task('webpack', gulp.series(typeScripts, webpackDev));

gulp.task(
	'build',
	gulp.series(
		clean,
		styles,
		typeScripts,
		gulp.parallel(
			() =>
				gulp
					.src(['./index.html'])
					.pipe(replace(/ts=\[\[0000000000\]\]/g, `ts=${new Date().valueOf()}`))
					.pipe(gulp.dest(sDistDir)),
			() =>
				gulp
					.src('css/**/*.css')
					.pipe(cleanCSS())
					.pipe(gulp.dest(`${sDistDir}/css`)),
			webpackProd
		)
	)
);
// Оставлю это пока тут
// gulp.src(['./**/*.php', '!./internet/**/*.php', '!./dist/**/*.php', '!./index.php'])
// .pipe(gulp.dest(sDistDir)),

let development = gulp.series(styles, typeScripts, webpackDev, watch);
gulp.task('default', development);

function runDevWebPack(sSource, sEntry) {
	return gulp
		.src(sSource)
		.pipe(plumber())
		.pipe(
			webpack({
				entry: {
					main: sEntry,
				},
				mode: 'development',
				output: {
					filename: '[name].bundle.js',
					// path: __dirname + '/js'
				},
				optimization: {
					splitChunks: {
						chunks: 'all',
					},
					usedExports: true,
					providedExports: true,
					sideEffects: false,
				},
				devtool: 'source-map',
				// plugins: [
				// 	new MomentLocalesPlugin({
				// 		localesToKeep: ['uk'],
				// 	}),
				// ],
			})
		)
		.pipe(gulp.dest('js'))
		.pipe(
			browserSync.reload({
				stream: true,
			})
		);
}

function runProdWebPack(sSource, sEntry, sDestination) {
	return gulp
		.src(sSource)
		.pipe(plumber())
		.pipe(
			webpack({
				entry: {
					main: sEntry,
				},
				mode: 'production',
				output: {
					filename: '[name].bundle.js',
				},
				optimization: {
					splitChunks: {
						chunks: 'all',
					},
				},
				// plugins: [
				// 	new MomentLocalesPlugin({
				// 		localesToKeep: ['uk'],
				// 	}),
				// ],
			})
		)
		.pipe(gulp.dest(sDestination));
}
