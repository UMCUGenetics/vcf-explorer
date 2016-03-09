import {Component, OnInit} from 'angular2/core';

import {VariantsService} from '../services/variants.service';

@Component({
  selector: 'variants',
  templateUrl:'/static/app/variant/components/variants.component.html',
  providers: [VariantsService]
})
export class VariantsComponent implements OnInit {
  variants: any[];

  constructor(private _variantsService: VariantsService) { }

  getVariants() {
    this._variantsService.getVariants().subscribe(
      variants => this.variants = variants
    );
  }

  ngOnInit() { this.getVariants(); }

}
