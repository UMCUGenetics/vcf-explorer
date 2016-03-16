import {Component, OnInit} from 'angular2/core';

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
export class SamplesComponent {
  private gridOptions: GridOptions;
  private samples: any[];
  private columnDefs: any[];

  constructor(private _sampleService: SamplesService) {
    this.gridOptions = <GridOptions>{};
    this.getSamples();
    this.createColumnDefs();
  }

  private getSamples() {
    this._sampleService.getSamples().subscribe(
      samples => this.samples = samples
    );
  }

  private createColumnDefs() {
    this.columnDefs = [
      {headerName: "Name", field: "_id",
        cellRenderer: function(params: any) {
          // Should use router-link here!
          return '<a href="/sample/'+params.value+'">'+params.value+'</a>';
        }
      },
      {headerName: "VCF", field: "vcf_files"},
    ];
  }

}
