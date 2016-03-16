import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class SamplesService {
  constructor (private http: Http) {}

  private _samplesUrl = '/api/sample/';  // URL to web api

  getSamples () {
    return this.http.get(this._samplesUrl)
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
