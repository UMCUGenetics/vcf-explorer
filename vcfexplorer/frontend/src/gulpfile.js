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
    .pipe(gulp.dest('../static/js/app'));
});

// copy dependencies
gulp.task('copy:libs', ['clean'], function() {
  return gulp.src([
      'node_modules/angular2/bundles/angular2-polyfills.js',
      'node_modules/systemjs/dist/system.src.js',
      'node_modules/rxjs/bundles/Rx.js',
      'node_modules/angular2/bundles/angular2.dev.js',
    ])
    .pipe(gulp.dest('../static/js/lib'))
});

// copy static assets - i.e. non TypeScript compiled source
gulp.task('copy:assets', ['clean'], function() {
  return gulp.src(['app/**/*', '!app/**/*.ts'], { base : './' })
    .pipe(gulp.dest('../static/js/app'))
});

// copy static assets - i.e. non TypeScript compiled source
gulp.task('copy:index', ['clean'], function() {
  return gulp.src(['index.html'], { base : './' })
    .pipe(gulp.dest('../templates'))
});

gulp.task('build', ['compile','copy:libs','copy:assets','copy:index']);
gulp.task('default', ['build']);
