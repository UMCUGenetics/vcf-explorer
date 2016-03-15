import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class VCFService {
  constructor (private http: Http) {}

  private _vcfUrl = '/api/vcf/';  // URL to web api
  getVCF(vcf_name: string) {
    return this.http.get(this._vcfUrl+vcf_name)
                    .map(res => res.json())
                    .catch(this.handleError);
  }
  getVCFVariants(vcf_name: string) {
    return this.http.get(this._vcfUrl+vcf_name+'/variants')
                    .map(res => res.json())
                    .catch(this.handleError);
  }
  private handleError (error: Response) {
    console.error(error);
    return Observable.throw(error.json().error || 'Server error');
  }
}
