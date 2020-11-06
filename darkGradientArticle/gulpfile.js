const gulp = require("gulp");
let browserSync = require("browser-sync").create();
const autoprefixer = require("gulp-autoprefixer");
const csslint = require("gulp-csslint");
const sass = require("gulp-sass");
const plumber = require("gulp-plumber");

let paths = {
	styles: {
		src: ["src/css/*.sass", "src/css/*.scss"],
		dest: "css",
	},
	// scripts: {
	// 	src: ["src/js/**/*.ts", "src/js/**/*.tsx", "!src/**/*.d.ts"],
	// 	dest: "js",
	// },
};

const styles = () =>
	gulp
		.src(paths.styles.src)
		.pipe(plumber())
		.pipe(sass().on("error", sass.logError))
		.pipe(
			csslint({
				lookup: false,
				ids: false,
				shorthand: true,
				"order-alphabetical": false,
				"qualified-headings": false,
				"box-model": false,
				"adjoining-classes": false,
				important: false,
			})
		)
		.pipe(csslint.formatter())
		.pipe(autoprefixer({}))
		.pipe(gulp.dest(paths.styles.dest))
		.pipe(browserSync.reload({ stream: true }));

function watch() {
	browserSync.init({
		server: true,
		files: ["css/*.css", "*.html"],
	});
	gulp.watch(paths.styles.src, styles);
	gulp.watch("./index.html").on("change", browserSync.reload);
}

gulp.task("sass", styles);

let development = gulp.series(styles, watch);
gulp.task("default", development);

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
