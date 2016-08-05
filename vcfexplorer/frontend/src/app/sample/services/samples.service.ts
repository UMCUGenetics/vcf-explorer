import {Injectable} from '@angular/core';
import {Http, Response} from '@angular/http';
import {Observable} from 'rxjs/Observable';

@Injectable()
export class SamplesService {
  constructor (private http: Http) {}

  private _samplesUrl = '/api/samples/';  // URL to web api

  getSamples (limit=20, offset=0) {
    return this.http.get(this._samplesUrl+"?limit="+limit+"&offset="+offset)
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
