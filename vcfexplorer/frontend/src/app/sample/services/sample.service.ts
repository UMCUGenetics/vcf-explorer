import {Injectable} from '@angular/core';
import {Http, Response} from '@angular/http';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class SampleService {
  constructor (private http: Http) {}

  private _sampleUrl = '/api/samples/';  // URL to web api

  getSample(sampleName: string) {
    return this.http.get(this._sampleUrl+sampleName)
                    .map(res => res.json())
                    .catch(this.handleError);
  }
  getSampleVariants(sampleName: string) {
    return this.http.get(this._sampleUrl+sampleName+'/variants')
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
