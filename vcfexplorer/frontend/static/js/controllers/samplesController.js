angular
  .module('vcfExplorerApp')
  .controller('samplesController', samplesController);

samplesController.$inject = ['samplesService','utilityService'];

function samplesController(samplesService, utilityService) {
  var vm = this;

  // Define columns
  var columnDefs = [
    {headerName: "Name", field: "samples", cellRenderer: function(params) {
      return '<a href="/#/samples/'+params.value+'">'+params.value+'</a>';
    }},
    {headerName: "VCF", field: "vcf_file"},
    {headerName: "Date", field: "upload_date", valueGetter: utilityService.getUploadDate}
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    angularCompileRows: false,
    ready: function(){ activate(); }
  };

  // Get Samples functions
  function activate() {
    return getSamples().then(function() {
      console.log('Activated Samples View');
    });
  }

  function getSamples() {
    return samplesService.getSamples()
      .then(function(data) {
        vm.gridOptions.rowData = data;
        vm.gridOptions.api.onNewRows();
        vm.gridOptions.api.sizeColumnsToFit();
      });
  }
};
