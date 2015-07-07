angular
  .module('vcfExplorerApp')
  .factory('runService', runService);

runService.$inject = ['$http'];

function runService($http, runName){
  return {
    getRunVariants: getRunVariants,
    getRun: getRun
  };

  function getRunVariants(runName) {
    return $http.get('/api/runs/'+runName+'/variants/')
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
