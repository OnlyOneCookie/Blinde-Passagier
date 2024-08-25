import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from "../../environments/environment";
import { TransferUtils } from '../utils/transfer.utils';

@Injectable({
  providedIn: 'root'
})
export class TransferService {
  private apiUrl = 'https://journey-maps.api.sbb.ch/v1';
  private apiKey = environment.apiKey;

  constructor(private http: HttpClient) { }

  getStations(): Observable<any[]> {
    return this.http.get<any>('assets/stations.json').pipe(
      map(data => data.map((station: any) => ({
        id: station.operatingpointkilometermasternumber,
        name: station.designationofficial
      })))
    );
  }

  getInstructions(stationId: number, fromTrack: string, toTrack: string): Observable<string[]> {
    const params = {
      client: 'webshop',
      clientVersion: 'latest',
      lang: 'en',
      fromStationID: stationId,
      toStationID: stationId,
      fromTrack: fromTrack,
      toTrack: toTrack,
      accessible: 'true'
    };

    return this.http.get(`${this.apiUrl}/transfer`, {
      headers: { 'X-API-Key': this.apiKey },
      params: params
    }).pipe(
      map((response: any) => TransferUtils.generateInstructions(response.features))
    );
  }
}
