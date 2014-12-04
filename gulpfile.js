var gulp       = require('gulp'),
    sass       = require('gulp-sass'),
    prefix     = require('gulp-autoprefixer'),
    livereload = require('gulp-livereload');


gulp.task('theme', function() {

  return gulp.src('zinnia/static/zinnia/theme/sass/**/*.scss')
         .pipe(sass({errLogToConsole: true}))
         .pipe(prefix())
         .pipe(gulp.dest('zinnia/static/zinnia/theme/css'));
});

gulp.task('admin-dashboard', function() {

  return gulp.src('zinnia/static/zinnia/admin/dashboard/sass/*.scss')
         .pipe(sass({errLogToConsole: true}))
         .pipe(prefix())
         .pipe(gulp.dest('zinnia/static/zinnia/admin/dashboard/css'));
});

gulp.task('watch', function() {

  livereload.listen();

  gulp.watch(['zinnia/static/zinnia/**/*',
              'zinnia/templates/**/*']).on('change', livereload.changed);

  gulp.watch('zinnia/static/zinnia/theme/sass/**/*.scss', ['theme']);
  gulp.watch('zinnia/static/zinnia/admin/dashboard/sass/*.scss', ['admin-dashboard']);

});


gulp.task('default', ['theme', 'admin-dashboard', 'watch']);
