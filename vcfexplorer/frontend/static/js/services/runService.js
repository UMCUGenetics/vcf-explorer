angular
  .module('vcfExplorerApp')
  .factory('runService', runService);

runService.$inject = ['$http'];

function runService($http, runName){
  return {
    getRunVariants: getRunVariants
  };

  function getRunVariants(runName) {
    return $http.get('/api/runs/'+runName+'/variants/')
      .then(getRunVariantsComplete)
      .catch(getRunVariantsRunsFailed);

    function getRunVariantsComplete(response){
      return response.data;
    }

    function getRunVariantsRunsFailed(error){
      console.log('Failed getRunVariants.' + error.data)
    }
  }
}
