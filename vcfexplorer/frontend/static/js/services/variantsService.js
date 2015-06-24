angular
  .module('vcfExplorerApp')
  .factory('variantsService', variantsService);

variantsService.$inject = ['$http'];

function variantsService($http){
  return {
    getVariants: getVariants
  };

  function getVariants() {
    return $http.get('/api/variants/')
      .then(getVariantsComplete)
      .catch(getVariantsFailed);

    function getVariantsComplete(response){
      return response.data;
    }

    function getVariantsFailed(error){
      console.log('Failed getVariants.' + error.data)
    }
  }
}
