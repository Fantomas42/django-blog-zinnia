var gulp       = require('gulp'),
    sass       = require('gulp-sass'),
    prefix     = require('gulp-autoprefixer'),
    livereload = require('gulp-livereload');

var HTML       = 'zinnia/templates/**/*.html',
    IMG        = 'zinnia/static/zinnia/img/*',
    JS         = 'zinnia/static/zinnia/js/**/*.js',
    SASS       = 'zinnia/static/zinnia/sass/**/*.scss',
    CSS        = 'zinnia/static/zinnia/css/*.css';

gulp.task('sass', function() {

  return gulp.src(SASS)
         .pipe(sass({errLogToConsole: true}))
         .pipe(prefix())
         .pipe(gulp.dest('zinnia/static/zinnia/css'));
});

gulp.task('admin-dashboard', function() {

  return gulp.src('zinnia/static/zinnia/admin/dashboard/sass/*.scss')
         .pipe(sass({errLogToConsole: true}))
         .pipe(prefix())
         .pipe(gulp.dest('zinnia/static/zinnia/admin/dashboard/css'));
});

gulp.task('watch', function() {

  var server = livereload();

  gulp.watch([CSS, JS, IMG], function(file) {
    server.changed(file.path);
  });

  gulp.watch(HTML, function(file) {
    server.changed('.');
  });

  gulp.watch(SASS, ['sass']);

});


gulp.task('default', ['sass', 'admin-dashboard', 'watch']);
