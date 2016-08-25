
/**
 * System configuration for Angular 2 samples
 * Adjust as necessary for your application needs.
 * Override at the last minute with global.filterSystemConfig (as plunkers do)
 */
(function(global) {

  // map tells the System loader where to look for things
  var map = {
    'app':                        'static/app', // 'dist',
    'rxjs':                       'static/js/lib/rxjs',
    '@angular':                   'static/js/lib/@angular',
    'ag-grid-ng2':                'static/js/lib/ag-grid-ng2',
    'ag-grid':                    'static/js/lib/ag-grid'
  };

  // packages tells the System loader how to load when no filename and/or no extension
  var packages = {
    'app':                        { main: 'main.js',  defaultExtension: 'js' },
    'rxjs':                       { defaultExtension: 'js' },
    'ag-grid-ng2': { defaultExtension: 'js' },
    'ag-grid': { defaultExtension: 'js' },
  };

  var angularPackageNames = [
    'common',
    'compiler',
    'core',
    'http',
    'platform-browser',
    'platform-browser-dynamic',
    'router-deprecated',
    'testing',
    'upgrade',
  ];

  // Add package entries for angular packages
  angularPackageNames.forEach(function(pkgName) {
    packages['@angular/'+pkgName] = { main: 'bundles/' + pkgName + '.umd.js', defaultExtension: 'js' };
  });

  var config = {
    map: map,
    packages: packages
  };

  System.config(config);

})(this);
