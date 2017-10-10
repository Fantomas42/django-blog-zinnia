var browserSync = require('browser-sync').create(),
    gulp        = require('gulp'),
    prefix      = require('gulp-autoprefixer'),
    sass        = require('gulp-sass'),
    sourcemaps  = require('gulp-sourcemaps');

var HTML       = 'zinnia/templates/**/*.html',
    THEME      = 'zinnia/static/zinnia/theme/sass/**/*.scss',
    DASHBOARD  = 'zinnia/static/zinnia/admin/dashboard/sass/*.scss';

gulp.task('theme', function() {
  browserSync.notify('Compiling theme, please wait !');

  return gulp.src(THEME)
         .pipe(sourcemaps.init())
         .pipe(sass().on('error', sass.logError))
         .pipe(prefix())
         .pipe(sourcemaps.write())
         .pipe(gulp.dest('zinnia/static/zinnia/theme/css'))
         .pipe(browserSync.stream());
});

gulp.task('dashboard', function() {
  browserSync.notify('Compiling dashboard, please wait !');

  return gulp.src(DASHBOARD)
         .pipe(sourcemaps.init())
         .pipe(sass().on('error', sass.logError))
         .pipe(prefix())
         .pipe(sourcemaps.write())
         .pipe(gulp.dest('zinnia/static/zinnia/admin/dashboard/css'))
         .pipe(browserSync.stream());
});

gulp.task('serve', function() {

  browserSync.init({
        proxy: 'localhost:8000',
        serveStatic: ['zinnia/static']
  });

  gulp.watch(HTML).on('change', browserSync.reload);
  gulp.watch(THEME, ['theme']);
  gulp.watch(DASHBOARD, ['dashboard']);

});

gulp.task('default', ['serve']);