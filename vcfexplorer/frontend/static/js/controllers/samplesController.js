angular
  .module('vcfExplorerApp')
  .controller('samplesController', samplesController);

samplesController.$inject = ['samplesService'];

function samplesController(samplesService) {
  var vm = this;

  var columnDefs = [
    {headerName: "Name", field: "samples", cellRenderer: function(params) {
      return '<a href="/#/samples/'+params.data.samples+'">'+params.data.samples+'</a>';
    }},
    {headerName: "VCF", field: "vcf_file"},
    {headerName: "Date", field: "upload_date"}
  ];

  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    angularCompileRows: false,
    ready: function(){ activate(); }
  };

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
