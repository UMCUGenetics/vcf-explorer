import {Component, OnInit} from '@angular/core';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {SamplesService} from '../services/samples.service';

@Component({
    selector: 'samples',
    templateUrl:'/static/app/sample/components/samples.component.html',
    directives: [AgGridNg2],
    providers: [SamplesService]
})
//export class SamplesComponent implements OnInit {
export class SamplesComponent implements OnInit {
    private gridOptions: GridOptions;
    private samples: any[];
    private columnDefs: any[];

    constructor(private _sampleService: SamplesService) {}

    ngOnInit(){
        this.gridOptions = <GridOptions>{};
        this.gridOptions.datasource = this.dataSource;
        this.createColumnDefs();
    }

    dataSource = {
        pageSize: 1,
        overflowSize: 100,

        getRows: (params: any) => {
            var limit = params.endRow - params.startRow;
            var offset = params.startRow;
            this._sampleService.getSamples(limit,offset).subscribe(rowData => {
                var rowsThisPage = rowData;
                var lastRow = -1;
                // call the success callback
                params.successCallback(rowsThisPage, lastRow);
            });
        }
    }

    private createColumnDefs() {
        this.columnDefs = [
            {headerName: "Name", field: "_id", cellRenderer: function(params: any) {
                // Should use router-link here!
                return '<a href="/sample/'+params.value+'">'+params.value+'</a>';
                }
            },
            {headerName: "VCF", field: "vcf_files"},
        ];
    }
}
