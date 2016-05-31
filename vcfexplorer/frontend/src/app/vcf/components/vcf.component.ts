import {Component, OnInit} from '@angular/core';
import {RouteParams} from '@angular/router-deprecated';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {VCFService} from '../services/vcf.service';

@Component({
  selector: 'vcfs',
  templateUrl:'/static/app/vcf/components/vcf.component.html',
  directives: [AgGridNg2],
  providers: [VCFService]
})
export class VCFComponent implements OnInit {
  private gridOptions: GridOptions;
  private vcf: any[];
  private vcf_variants: any[];
  private columnDefs: any[];

  constructor(
    private _VCFService: VCFService,
    private _routeParams: RouteParams) {
    }

  ngOnInit() {
    let vcfName = this._routeParams.get('name');
    this.gridOptions = <GridOptions>{};
    this.getVCF(vcfName);
    this.getVCFVariants(vcfName);
    this.createColumnDefs();
  }

  private getVCF(vcfName: string) {
    this._VCFService.getVCF(vcfName).subscribe(
      vcf => this.vcf = vcf
    );
  }

  private getVCFVariants(vcfName: string) {
    this._VCFService.getVCFVariants(vcfName).subscribe(
      vcf_variants => this.vcf_variants = vcf_variants
    );
  }

  private createColumnDefs() {
    this.columnDefs = [
      {headerName: "Chr", field: "chr"},
      {headerName: "Pos", field: "pos"},
      {headerName: "Ref", field: "ref"},
      {headerName: "Alt", field: "alt"},
      {headerName: "Samples", field: "samples"},
    ];
  }

}
