angular
  .module('vcfExplorerApp')
  .controller('runsController', runsController);

runsController.$inject = ['runsService','utilityService'];

function runsController(runsService, utilityService) {
  var vm = this;

  // Define columns
  var columnDefs = [
    {headerName: "Name", field: "name", cellRenderer: function(params) {
      return '<a href="/#/runs/'+params.value+'">'+params.value+'</a>';
    }},
    {headerName: "VCF", field: "vcf_file"},
    {headerName: "Samples", field: "samples"},
    {headerName: "Date", field: "upload_date", valueGetter: utilityService.getUploadDate}
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
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
