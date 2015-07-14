angular
  .module('vcfExplorerApp')
  .factory('sampleService', sampleService);

sampleService.$inject = ['$http'];

function sampleService($http, sampleName){
  return {
    getSampleVariants: getSampleVariants,
    getSample: getSample
  };

  function getSampleVariants(sampleName) {
    return $http.get('/api/samples/'+sampleName+'/variants/')
      .then(getSampleVariantsComplete)
      .catch(getSampleVariantsFailed);

    function getSampleVariantsComplete(response){
      return response.data;
    }

    function getSampleVariantsFailed(error){
      console.log('Failed getSampleVariants.' + error.data)
    }
  }

  function getSample(sampleName) {
    return $http.get('/api/samples/'+sampleName)
      .then(getSampleComplete)
      .catch(getSampleFailed);

    function getSampleComplete(response){
      return response.data;
    }

    function getSampleFailed(error){
      console.log('Failed getSampleVariants.' + error.data)
    }
  }
}
