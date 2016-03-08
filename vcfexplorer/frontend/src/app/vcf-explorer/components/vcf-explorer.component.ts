import {Component} from 'angular2/core';
import {RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS} from 'angular2/router';
import {VCFsComponent} from '../../vcfs/components/vcfs.component';
import {SamplesComponent} from '../../samples/components/samples.component';
import {VariantsComponent} from '../../variants/components/variants.component';

@Component({
    selector: 'vcf-explorer',
    templateUrl: 'static/app/vcf-explorer/components/vcf-explorer.component.html',
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS]
})
@RouteConfig([
  { path: '/vcfs', name: 'VCFs', component: VCFsComponent},
  { path: '/samples', name: 'Samples', component: SamplesComponent},
  { path: '/variants', name: 'Variants', component: VariantsComponent}
])
export class AppComponent { }
