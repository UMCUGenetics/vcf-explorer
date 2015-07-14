angular
  .module('vcfExplorerApp')
  .controller('runsController', runsController);

runsController.$inject = ['runsService'];

function runsController(runsService) {
  var vm = this;

  // Define columns
  var columnDefs = [
    {headerName: "Name", field: "name", cellRenderer: function(params) {
      return '<a href="/#/runs/'+params.data.name+'">'+params.data.name+'</a>';
    }},
    {headerName: "VCF", field: "vcf_file"},
    {headerName: "Samples", field: "samples"}
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    angularCompileRows: false,
    ready: function(){ activate(); }
  };

  // Get Runs functions
  function activate() {
    return getRuns().then(function() {
      console.log('Activated Runs View');
    });
  }

  function getRuns() {
    return runsService.getRuns()
      .then(function(data) {
        vm.gridOptions.rowData = data;
        vm.gridOptions.api.onNewRows();
        vm.gridOptions.api.sizeColumnsToFit();
      });
  }
};
