angular
  .module('vcfExplorerApp')
  .controller('variantsController', variantsController);

variantsController.$inject = ['variantsService'];

function variantsController(variantsService) {
  var vm = this;
  vm.data = []

  // Define columns
  var columnDefs = [
    {headerName: "ID", field: "_id", filter: 'text', sort: 'asc', cellRenderer: function(params){
      return '<a href="/#/variants/'+params.value+'">'+params.value+'</a>';
    }},
    {headerName: "Chr", field: "chr"},
    {headerName: "Pos", field: "pos", filter: 'number'},
    {headerName: "Ref", field: "ref"},
    {headerName: "Alt", field: "alt"},
    {headerName: "Alt AC", field: "alt_ac", headerTooltip: "Filtered alternative allele count", filter: 'number'},
    {headerName: "Alt AF", valueGetter: 'data.alt_ac / data.total_ac', headerTooltip: "Filtered alternative allele frequency", filter: 'number'},
    {headerName: "# Samples", field: "samples", headerTooltip: "Filtered sample count", valueGetter: 'data.alt_ac / 2', filter: 'number'},
  ];

  // Setup grid
  vm.gridOptions = {
    columnDefs: columnDefs,
    rowData: null,
    enableSorting: true,
    enableFilter: true,
    ready: function(){
      activate();
    },
  };

  // Get variants function
  function activate() {
    return getVariants().then(function() {
      console.log('Activated Variants View');
    });
  }

  function getVariants() {
    return variantsService.getVariants()
      .then(function(data) {
        vm.gridOptions.rowData = data;
        vm.gridOptions.api.onNewRows();
        vm.gridOptions.api.sizeColumnsToFit();
      });
  }
};
