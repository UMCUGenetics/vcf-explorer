import {Component} from 'angular2/core';
import {RouteParams} from 'angular2/router';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {VCFService} from '../services/vcf.service';

@Component({
  selector: 'vcfs',
  templateUrl:'/static/app/vcf/components/vcf.component.html',
  directives: [AgGridNg2],
  providers: [VCFService]
})
export class VCFComponent {
  private gridOptions: GridOptions;
  private vcf: any[];
  private vcf_variants: any[];
  private columnDefs: any[];

  constructor(
    private _VCFService: VCFService,
    private _routeParams: RouteParams)
  {
    let vcf_name = this._routeParams.get('name');
    this.gridOptions = <GridOptions>{};
    this.getVCF(vcf_name);
    this.getVCFVariants(vcf_name);
    this.createColumnDefs();
  }

  private getVCF(vcf_name: string) {
    this._VCFService.getVCF(vcf_name).subscribe(
      vcf => this.vcf = vcf
    );
  }

  private getVCFVariants(vcf_name: string) {
    this._VCFService.getVCFVariants(vcf_name).subscribe(
      vcf_variants => this.vcf_variants = vcf_variants
    );
  }

  private createColumnDefs() {
    this.columnDefs = [
      {headerName: "CHR", field: "chr"},
      {headerName: "Pos", field: "pos"},
      {headerName: "Ref", field: "ref"},
      {headerName: "Alt", field: "alt"},
      {headerName: "Samples", field: "samples"},
    ];
  }

}
