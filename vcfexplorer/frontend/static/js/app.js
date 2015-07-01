angular
  .module('vcfExplorerApp', [
    'angularGrid',
    'ngRoute'
  ])
  .config(function ($routeProvider, $locationProvider) {

    $routeProvider
      .when('/', {
        //controller: 'homeController',
        templateUrl: '/static/partials/home.html'
      })
      .when('/runs', {
        controller: 'runsController',
        templateUrl: '/static/partials/runs.html'
      })
      .when('/samples', {
        controller: 'samplesController',
        templateUrl: '/static/partials/samples.html'
      })
      .when('/variants', {
        controller: 'variantsController',
        templateUrl: '/static/partials/variants.html'
      })
      .otherwise({
        redirectTo: '/'
      });

    // use the HTML5 History API
    // $locationProvider.html5Mode(true);
});
