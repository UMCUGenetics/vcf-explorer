import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class VCFService {
  constructor (private http: Http) {}

  private _vcfUrl = '/api/vcf/';  // URL to web api
  getVCF(vcfName: string) {
    return this.http.get(this._vcfUrl+vcfName)
                    .map(res => res.json())
                    .catch(this.handleError);
  }
  getVCFVariants(vcfName: string) {
    return this.http.get(this._vcfUrl+vcfName+'/variants')
                    .map(res => res.json())
                    .catch(this.handleError);
  }
  private handleError (error: Response) {
    // send the error to some remote logging infrastructure
    // instead of just logging it to the console
    console.error(error);
    return Observable.throw(error.json().error || 'Server error');
  }
}
