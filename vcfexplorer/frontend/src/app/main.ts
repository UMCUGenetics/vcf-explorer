import {bootstrap}    from 'angular2/platform/browser';
import {HTTP_PROVIDERS} from 'angular2/http';

import {AppComponent} from './vcf-explorer/components/vcf-explorer.component';

// Add all operators to Observable
import 'rxjs/Rx';

bootstrap(AppComponent, [HTTP_PROVIDERS]);
