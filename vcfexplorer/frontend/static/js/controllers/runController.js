angular
  .module('vcfExplorerApp')
  .controller('runController', runController);

runController.$inject = ['runService', '$routeParams'];

function runController(runService, $routeParams) {
  var vm = this;

  vm.runName = $routeParams.runName

  var columnDefs = [
    {headerName: "Chr", field: "chr"},
    {headerName: "Pos", field: "pos"},
    {headerName: "Ref", field: "ref"},
    {headerName: "Alt", field: "alt"},
    {headerName: "Samples", field: "samples"},
  ];

  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    ready: function(){ activateRunVariants(vm.runName); },
  };

  function activateRunVariants(runName) {
    return getRunVariants(runName).then(function() {
      console.log('Activated RunVariants View');
    });
  }

  function getRunVariants(runName) {
    return runService.getRunVariants(runName)
      .then(function(data) {
        vm.gridOptions.rowData = data;
        vm.gridOptions.api.onNewRows();
        vm.gridOptions.api.sizeColumnsToFit();
      });
  }
};
