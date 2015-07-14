angular
  .module('vcfExplorerApp')
  .controller('sampleController', sampleController);

sampleController.$inject = ['sampleService', '$routeParams'];

function sampleController(sampleService, $routeParams) {
  var vm = this;

  // Get sampleName from arguments and get sample metadata
  vm.sampleName = $routeParams.sampleName
  vm.sample = {};

  // Define columns
  var columnDefs = [
    {headerName: "Chr", field: "chr"},
    {headerName: "Pos", field: "pos", filter: 'number'},
    {headerName: "Ref", field: "ref"},
    {headerName: "Alt", field: "alt"},
    {headerName: "GT", field: "gt", valueGetter: 'data.samples[0].GT'},
    {headerName: "GQ", field: "gq", valueGetter: 'data.samples[0].GQ'},
    {headerName: "DP", field: "dp", valueGetter: 'data.samples[0].DP'},
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
      activateSampleVariants(vm.sampleName);
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
  function activateSampleVariants(sampleName) {
    return getSampleVariants(sampleName).then(function() {
      console.log('Activated SampleVariants View');
    });
  }

  function getSampleVariants(sampleName) {
    return sampleService.getSampleVariants(sampleName)
    .then(function(data) {
      vm.gridOptions.rowData = data;
      vm.gridOptions.api.onNewRows();
      vm.gridOptions.api.sizeColumnsToFit();
    });
  }

};
