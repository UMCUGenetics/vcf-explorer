angular
  .module('vcfExplorerApp')
  .factory('samplesService', samplesService);

samplesService.$inject = ['$http'];

function samplesService($http){
  return {
    getSamples: getSamples
  };

  function getSamples() {
    return $http.get('/api/samples/')
      .then(getSamplesComplete)
      .catch(getSamplesFailed);

    function getSamplesComplete(response){
      return response.data;
    }

    function getSamplesFailed(error){
      console.log('Failed getSamples.' + error.data)
    }
  }
}
