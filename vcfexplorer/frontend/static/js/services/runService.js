angular
  .module('vcfExplorerApp')
  .factory('runService', runService);

runService.$inject = ['$http'];

function runService($http, runName){
  return {
    getRunVariants: getRunVariants,
    getRun: getRun
  };

  function getRunVariants(runName, filtered_vars) {
    var req = {
      method: 'GET',
      url: '/api/runs/'+runName+'/variants/',
      params: {'filtered_vars':filtered_vars},
    };

    return $http(req)
      .then(getRunVariantsComplete)
      .catch(getRunVariantsFailed);

    function getRunVariantsComplete(response){
      return response.data;
    }

    function getRunVariantsFailed(error){
      console.log('Failed getRunVariants.' + error.data)
    }
  }

  function getRun(runName) {
    return $http.get('/api/runs/'+runName)
      .then(getRunComplete)
      .catch(getRunFailed);

    function getRunComplete(response){
      return response.data;
    }

    function getRunFailed(error){
      console.log('Failed getRunVariants.' + error.data)
    }
  }
}
