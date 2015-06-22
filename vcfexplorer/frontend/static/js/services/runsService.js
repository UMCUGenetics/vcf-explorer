angular
  .module('vcfExplorerApp')
  .factory('runsService', runsService);

runsService.$inject = ['$http'];

function runsService($http){
  return {
    getRuns: getRuns
  };

  function getRuns() {
    return $http.get('/api/runs/')
      .then(getRunsComplete)
      .catch(getRunsFailed);

    function getRunsComplete(response){
      return response.data;
    }

    function getRunsFailed(error){
      console.log('Failed getRuns.' + error.data)
    }
  }
}
