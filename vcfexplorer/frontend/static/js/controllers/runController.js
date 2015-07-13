angular
  .module('vcfExplorerApp')
  .controller('runController', runController);

runController.$inject = ['runService', '$routeParams'];

function runController(runService, $routeParams) {
  var vm = this;

  // Get runName from arguments and get run metadata
  vm.runName = $routeParams.runName
  vm.run = {};

  // Define columns
  var columnDefs = [
    {headerName: "Chr", field: "chr"},
    {headerName: "Pos", field: "pos", filter: 'number'},
    {headerName: "Ref", field: "ref"},
    {headerName: "Alt", field: "alt"},
  ];

  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    enableSorting: true,
    enableFilter: true,
    ready: function(){
      activateRun(vm.runName);
      activateRunVariants(vm.runName);
    },
  };

  function activateRun(runName) {
    return getRun(runName).then(function() {
      console.log('Activated Run View');
    });
  }

  function getRun(runName) {
    return runService.getRun(runName)
      .then(function(data) {
        vm.run = data;
        // Add samples to columnDefs
        var index, len
        for (index=0, len=vm.run.samples.length; index < len; ++index){
          // This probably does not work correctly.
          // With 3 samples and 2 with a variant, then the representation is not correct anymore.
          // How to get correct data out?
          // Write valueGetter function, which gets data based on value of samples.id???
          sampleColumnDef = { headerName: vm.run.samples[index], field:vm.run.samples[index], valueGetter: 'data.samples['+index+'].GT' };
          vm.gridOptions.columnDefs = vm.gridOptions.columnDefs.concat(sampleColumnDef);
        };
        vm.gridOptions.api.onNewCols();
        vm.gridOptions.api.sizeColumnsToFit();
        return vm.run;
      });
  }

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
