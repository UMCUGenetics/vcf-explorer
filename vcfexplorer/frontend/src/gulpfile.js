const gulp = require('gulp');
const del = require('del');
const typescript = require('gulp-typescript');
const tscConfig = require('./tsconfig.json');
const sourcemaps = require('gulp-sourcemaps');

// clean the contents of the distribution directory
gulp.task('clean', function () {
  return del([
    '../static/**/*',
    '../templates/*'
  ],
  {
    force: true
  });
});

// TypeScript compile
gulp.task('compile', ['clean'], function () {
  return gulp
    .src(tscConfig.files)
    .pipe(sourcemaps.init())          // <--- sourcemaps
    .pipe(typescript(tscConfig.compilerOptions))
    .pipe(sourcemaps.write('.'))      // <--- sourcemaps
    .pipe(gulp.dest('../static/app'));
});

// copy js dependencies
gulp.task('copy:js_libs', ['clean'], function() {
  return gulp.src([
      'node_modules/angular2/bundles/angular2-polyfills.js',
      'node_modules/systemjs/dist/system.src.js',
      'node_modules/rxjs/bundles/Rx.js',
      'node_modules/angular2/bundles/angular2.dev.js',
      'node_modules/angular2/bundles/router.dev.js',
      'node_modules/angular2/bundles/http.dev.js',
      'node_modules/bootstrap/dist/js/bootstrap.min.js',
    ])
    .pipe(gulp.dest('../static/js/lib'))
});

// copy css dependencies
gulp.task('copy:css_libs', ['clean'], function() {
  return gulp.src([
      'node_modules/bootstrap/dist/css/bootstrap.min.css',
    ])
    .pipe(gulp.dest('../static/css/lib'))
});

// copy static assets - i.e. non TypeScript compiled source
gulp.task('copy:assets', ['clean'], function() {
  return gulp.src(['app/**/*', '!app/**/*.ts'], { base : './' })
    .pipe(gulp.dest('../static/'))
});

// copy css files
gulp.task('copy:css', ['clean'], function() {
  return gulp.src(['css/**/*'], { base : './' })
    .pipe(gulp.dest('../static/'))
});

// copy index.html
gulp.task('copy:index', ['clean'], function() {
  return gulp.src(['index.html'], { base : './' })
    .pipe(gulp.dest('../templates'))
});

gulp.task('build', ['compile','copy:js_libs','copy:css_libs','copy:assets','copy:css','copy:index']);
gulp.task('default', ['build']);
