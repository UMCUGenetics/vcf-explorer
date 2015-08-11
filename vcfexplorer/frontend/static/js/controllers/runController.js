angular
  .module('vcfExplorerApp')
  .controller('runController', runController);

runController.$inject = ['runService', '$routeParams'];

function runController(runService, $routeParams) {
  var vm = this;

  // Get runName from arguments
  vm.runName = $routeParams.runName
  vm.run = {};

  // Filtered variants checkbox
  vm.filterCheckbox = {
    value : ''
  };

  // Define columns
  var columnDefs = [
    {headerName: "Chr", field: "chr", sort: 'asc'},
    {headerName: "Pos", field: "pos", filter: 'number', sort: 'asc'},
    {headerName: "Ref", field: "ref"},
    {headerName: "Alt", field: "alt"},
    {headerName: "Filter", field: "filter"},
    {headerName: "Alt AC", field: "alt_ac", filter: 'number'},
    {headerName: "Alt AF", valueGetter: 'data.alt_ac / data.total_ac', filter: 'number'},
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    enableSorting: true,
    enableFilter: true,
    enableCellExpressions: true,
    ready: function(){
      activateRun(vm.runName);
      vm.activateRunVariants(vm.runName, vm.filterCheckbox['value']);
    },
  };

  // Get run (meta)data functions
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
        sampleColumnDef = { headerName: vm.run.samples[index], field:vm.run.samples[index], valueGetter: getVariant };
        vm.gridOptions.columnDefs = vm.gridOptions.columnDefs.concat(sampleColumnDef);
      };
      vm.gridOptions.api.onNewCols();
      vm.gridOptions.api.sizeColumnsToFit();
      return vm.run;
    });
  }

  // Get run variants functions
  // Available in $scope
  vm.activateRunVariants = function(runName, filtered_vars) {
    return getRunVariants(runName, filtered_vars).then(function() {
      console.log('Activated RunVariants View');
    });
  }

  function getRunVariants(runName, filtered_vars) {
    return runService.getRunVariants(runName, filtered_vars)
    .then(function(data) {
      vm.gridOptions.rowData = data;
      vm.gridOptions.api.onNewRows();
      vm.gridOptions.api.sizeColumnsToFit();
    });
  }

  // Valuegetter for sample genotype per variant.
  function getVariant(params) {
    for (index=0, len=params.data.samples.length; index < len; ++index){
      if(params.data.samples[index].id == params.colDef.field){
        return params.data.samples[index].GT
    }};
  };
};
