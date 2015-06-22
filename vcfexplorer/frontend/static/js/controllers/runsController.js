angular
  .module('vcfExplorerApp')
  .controller('runsController', runsController);

runsController.$inject = ['runsService'];

function runsController(runsService) {
  var runs = this;
  runs.data = []

  activate();

  function activate() {
    return getRuns().then(function() {
      console.log('Activated Runs View');
    });
  }

  function getRuns() {
    return runsService.getRuns()
      .then(function(data) {
        runs.data = data;
        return runs.data;
      });
  }
};
