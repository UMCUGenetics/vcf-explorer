angular
  .module('vcfExplorerApp')
  .factory('variantService', variantService);

variantService.$inject = ['$http'];

function variantService($http){
  return {
    getVariant: getVariant
  };

  function getVariant(variantID) {
    return $http.get('/api/variants/'+variantID)
      .then(getVariantComplete)
      .catch(getVariantFailed);

    function getVariantComplete(response){
      return response.data;
    }

    function getVariantFailed(error){
      console.log('Failed getVariant.' + error.data)
    }
  }
}
