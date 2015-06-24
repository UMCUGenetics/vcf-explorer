angular
  .module('vcfExplorerApp')
  .controller('samplesController', samplesController);

samplesController.$inject = ['samplesService'];

function samplesController(samplesService) {
  var vm = this;
  vm.data = []

  activate();

  function activate() {
    return getSamples().then(function() {
      console.log('Activated Samples View');
    });
  }

  function getSamples() {
    return samplesService.getSamples()
      .then(function(data) {
        vm.data = data;
        return vm.data;
      });
  }
};
