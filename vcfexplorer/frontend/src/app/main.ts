import {bootstrap}    from '@angular/platform-browser-dynamic';
import {HTTP_PROVIDERS} from '@angular/http';

import {AppComponent} from './vcf-explorer/components/vcf-explorer.component';

// Add all operators to Observable
import 'rxjs/Rx';

bootstrap(AppComponent, [HTTP_PROVIDERS]);
