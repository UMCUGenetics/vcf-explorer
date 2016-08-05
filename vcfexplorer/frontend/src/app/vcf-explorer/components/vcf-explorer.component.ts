import {Component, provide} from '@angular/core';
import {RouteConfig, ROUTER_DIRECTIVES, ROUTER_PROVIDERS} from '@angular/router-deprecated';
import {APP_BASE_HREF} from '@angular/common';
import {VCFsComponent} from '../../vcf/components/vcfs.component';
import {VCFComponent} from '../../vcf/components/vcf.component';
import {SamplesComponent} from '../../sample/components/samples.component';
import {SampleComponent} from '../../sample/components/sample.component';
import {VariantsComponent} from '../../variant/components/variants.component';

@Component({
    selector: 'vcf-explorer',
    templateUrl: 'static/app/vcf-explorer/components/vcf-explorer.component.html',
    directives: [ROUTER_DIRECTIVES],
    providers: [ROUTER_PROVIDERS, provide(APP_BASE_HREF, { useValue: '/' })]
})
@RouteConfig([
  { path: '/vcf', name: 'VCFs', component: VCFsComponent},
  { path: '/vcf/:name', name: 'VCF', component: VCFComponent},
  { path: '/sample', name: 'Samples', component: SamplesComponent},
  { path: '/sample/:name', name: 'Sample', component: SampleComponent},
  { path: '/variant', name: 'Variants', component: VariantsComponent}
])
export class AppComponent { }
