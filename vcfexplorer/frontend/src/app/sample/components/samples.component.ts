import {Component, OnInit} from 'angular2/core';

import {SamplesService} from '../services/samples.service';

@Component({
  selector: 'samples',
  templateUrl:'/static/app/sample/components/samples.component.html',
  providers: [SamplesService]
})
export class SamplesComponent implements OnInit {
  samples: any[];

  constructor(private _sampleService: SamplesService) { }

  getSamples() {
    this._sampleService.getSamples().subscribe(
      samples => this.samples = samples
    );
  }

  ngOnInit() { this.getSamples(); }

}
