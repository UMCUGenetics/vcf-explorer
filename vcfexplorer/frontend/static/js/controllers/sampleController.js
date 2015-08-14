angular
  .module('vcfExplorerApp')
  .controller('sampleController', sampleController);

sampleController.$inject = ['sampleService', '$routeParams'];

function sampleController(sampleService, $routeParams) {
  var vm = this;

  // Get sampleName from arguments
  vm.sampleName = $routeParams.sampleName
  vm.sample = {};

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
    {headerName: "Alt AC", field: "alt_ac", headerTooltip: "Filtered alternative allele count", filter: 'number'},
    {headerName: "Alt AF", valueGetter: 'data.alt_ac / data.total_ac', headerTooltip: "Filtered alternative allele frequency", filter: 'number'},
    {headerName: "GT", field: "gt", valueGetter: 'data.samples[0].GT'},
    {headerName: "GQ", field: "gq", valueGetter: 'data.samples[0].GQ'},
    {headerName: "DP", field: "dp", valueGetter: 'data.samples[0].DP'},
    {headerName: "AD", field: "ad", valueGetter: 'data.samples[0].AD'},
    {headerName: "Filter", field: "filter", valueGetter: 'data.samples[0].filter'},
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    enableSorting: true,
    enableFilter: true,
    ready: function(){
      activateSample(vm.sampleName);
      vm.activateSampleVariants(vm.sampleName, vm.filterCheckbox['value']);
    },
  };

  // Get Sample (meta)data functions
  function activateSample(sampleName) {
    return getSample(sampleName).then(function() {
      console.log('Activated Sample View');
    });
  }

  function getSample(sampleName) {
    return sampleService.getSample(sampleName)
      .then(function(data) {
      vm.sample = data;
      return vm.sample;
    });
  }

  // Get sample variants functions
  // Available in scope
   vm.activateSampleVariants = function(sampleName, filtered_vars) {
    return getSampleVariants(sampleName, filtered_vars).then(function() {
      console.log('Activated SampleVariants View');
    });
  }

  function getSampleVariants(sampleName, filtered_vars) {
    return sampleService.getSampleVariants(sampleName, filtered_vars)
    .then(function(data) {
      vm.gridOptions.rowData = data;
      vm.gridOptions.api.onNewRows();
      vm.gridOptions.api.sizeColumnsToFit();
    });
  }

};
