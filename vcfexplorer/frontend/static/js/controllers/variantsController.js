angular
  .module('vcfExplorerApp')
  .controller('variantsController', variantsController);

variantsController.$inject = ['variantsService'];

function variantsController(variantsService) {
  var vm = this;
  vm.data = []

  activate();

  function activate() {
    return getVariants().then(function() {
      console.log('Activated Variants View');
    });
  }

  function getVariants() {
    return variantsService.getVariants()
      .then(function(data) {
        vm.data = data;
        return vm.data;
      });
  }
};
