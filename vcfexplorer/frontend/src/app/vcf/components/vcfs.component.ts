import {Component, OnInit} from 'angular2/core';

import {VCFsService} from '../services/vcfs.service';

@Component({
  selector: 'vcfs',
  templateUrl:'/static/app/vcf/components/vcfs.component.html',
  providers: [VCFsService]
})
export class VCFsComponent implements OnInit {
  vcfs: any[];

  constructor(private _VCFsService: VCFsService) { }

  getVCFs() {
    this._VCFsService.getVCFs().subscribe(
      vcfs => this.vcfs = vcfs
    );
  }

  ngOnInit() { this.getVCFs(); }

}
