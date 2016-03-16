import {Component} from 'angular2/core';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {VCFsService} from '../services/vcfs.service';

@Component({
  selector: 'vcfs',
  templateUrl:'/static/app/vcf/components/vcfs.component.html',
  directives: [AgGridNg2],
  providers: [VCFsService]
})
export class VCFsComponent {
  private gridOptions: GridOptions;
  private vcfs: any[];
  private columnDefs: any[];

  constructor(private _VCFsService: VCFsService) {
    this.gridOptions = <GridOptions>{};
    this.getVCFs();
    this.createColumnDefs();
  }

  private getVCFs() {
    this._VCFsService.getVCFs().subscribe(
      vcfs => this.vcfs = vcfs
    );
  }

  private createColumnDefs() {
    this.columnDefs = [
      {headerName: "Name", field: "name",
        cellRenderer: function(params: any) {
          // Should use router-link here!
          return '<a href="/vcf/'+params.value+'">'+params.value+'</a>';
        }
      },
      {headerName: "VCF file", field: "vcf_file"},
      {headerName: "Samples", field: "samples"},
    ];
  }

}
