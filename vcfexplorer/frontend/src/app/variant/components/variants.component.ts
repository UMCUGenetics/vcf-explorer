import {Component} from 'angular2/core';

import {AgGridNg2} from 'ag-grid-ng2/main';
import {GridOptions} from 'ag-grid/main';

import {VariantsService} from '../services/variants.service';

@Component({
  selector: 'variants',
  templateUrl:'/static/app/variant/components/variants.component.html',
  directives: [AgGridNg2],
  providers: [VariantsService]
})
export class VariantsComponent {
  private gridOptions: GridOptions;
  private variants: any[];
  private columnDefs: any[];

  constructor(private _variantsService: VariantsService) {
    this.gridOptions = <GridOptions>{};
    this.getVariants();
    this.createColumnDefs();
  }

  private getVariants() {
    this._variantsService.getVariants().subscribe(
      variants => this.variants = variants
    );
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
