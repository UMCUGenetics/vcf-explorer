import {Component, OnInit} from 'angular2/core';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {VariantsService} from '../services/variants.service';

@Component({
  selector: 'variants',
  templateUrl:'/static/app/variant/components/variants.component.html',
  directives: [AgGridNg2],
  providers: [VariantsService]
})
export class VariantsComponent implements OnInit{
  private gridOptions: GridOptions;
  private columnDefs: any[];

  constructor(private _variantsService: VariantsService) {}

  ngOnInit(){
    this.gridOptions = <GridOptions>{};
    this.gridOptions.datasource = this.dataSource;
    this.createColumnDefs();
  }

  dataSource = {
      //rowCount : -1,
      pageSize: 10,
      overflowSize: 100,

      getRows: (params: any) => {
          var limit = params.endRow - params.startRow;
          var offset = params.startRow;
          this._variantsService.getVariants(limit,offset).subscribe(rowData => {
              //var rowsThisPage = rowData.slice(params.startRow, params.endRow);
              var rowsThisPage = rowData;
              var lastRow = -1;
              //if (rowData.length <= params.endRow) {
              //lastRow = rowData.length;
              //}
              // call the success callback
              params.successCallback(rowsThisPage, lastRow);
          });
      }
  }

  private createColumnDefs() {
    this.columnDefs = [
      {headerName: "ID", field: "_id",},
      {headerName: "CHR", field: "chr"},
      {headerName: "POS", field: "pos"},
      {headerName: "REF", field: "ref"},
      {headerName: "ALT", field: "alt"},
    ];
  }

}
