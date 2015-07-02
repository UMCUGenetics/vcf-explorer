angular
  .module('vcfExplorerApp')
  .controller('runsController', runsController);

runsController.$inject = ['runsService'];

function runsController(runsService) {
  var vm = this;

  var columnDefs = [
    {headerName: "Name", field: "name", template: '<a href="/#/runs/{{data.name}}">{{data.name}}</a>'},
    {headerName: "VCF", field: "vcf_file"},
    {headerName: "Samples", field: "samples"}
  ];

  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    angularCompileRows: true,
    ready: function(){ activate(); }
  };

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
