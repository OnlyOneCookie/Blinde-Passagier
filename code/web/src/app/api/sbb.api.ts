import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SbbApi {
  private apiUrl = 'https://journey-maps.api.sbb.ch';
  private apiKey = environment.apiKey;

  constructor(private http: HttpClient) { }

  get(endpoint: string, params: any): Observable<any> {
    const headers = new HttpHeaders().set('X-API-Key', this.apiKey);
    return this.http.get(`${this.apiUrl}/v1/${endpoint}`, { headers, params });
  }
}
