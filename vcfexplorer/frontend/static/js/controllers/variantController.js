angular
  .module('vcfExplorerApp')
  .controller('variantController', variantController);

variantController.$inject = ['variantService', '$routeParams'];

function variantController(variantService, $routeParams) {
  var vm = this;

  // Get variantName from arguments
  vm.variantID = $routeParams.variantID
  vm.variant = {};

  activateVariant(vm.variantID);

  // Get Variant (meta)data functions
  function activateVariant(variantID) {
    return getVariant(variantID).then(function() {
      console.log('Activated Variant View');
    });
  }

  function getVariant(variantID) {
    return variantService.getVariant(variantID)
      .then(function(data) {
      vm.variant = data;
      return vm.variant;
    });
  }
};
