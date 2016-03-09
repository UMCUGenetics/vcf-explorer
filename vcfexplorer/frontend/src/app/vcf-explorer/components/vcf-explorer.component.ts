import {Component} from 'angular2/core';
import {RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS} from 'angular2/router';
import {VCFsComponent} from '../../vcf/components/vcfs.component';
import {SamplesComponent} from '../../sample/components/samples.component';
import {VariantsComponent} from '../../variant/components/variants.component';

@Component({
    selector: 'vcf-explorer',
    templateUrl: 'static/app/vcf-explorer/components/vcf-explorer.component.html',
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS]
})
@RouteConfig([
  { path: '/vcf', name: 'VCFs', component: VCFsComponent},
  { path: '/sample', name: 'Samples', component: SamplesComponent},
  { path: '/variant', name: 'Variants', component: VariantsComponent}
])
export class AppComponent { }
