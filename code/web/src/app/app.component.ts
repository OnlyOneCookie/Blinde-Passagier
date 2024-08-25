import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SbbAutocompleteModule } from '@sbb-esta/angular/autocomplete';
import { SbbFormFieldModule } from '@sbb-esta/angular/form-field';
import { SbbInputModule } from '@sbb-esta/angular/input';
import { SbbButtonModule } from '@sbb-esta/angular/button';
import { TransferService } from './services/transfer.service';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { FormControl } from '@angular/forms';

interface Station {
  id: string;
  name: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SbbAutocompleteModule,
    SbbFormFieldModule,
    SbbInputModule,
    SbbButtonModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  stations: Station[] = [];
  filteredStations: Observable<Station[]> | undefined;
  stationControl = new FormControl('');
  fromTrack: string = '';
  toTrack: string = '';
  instructions: string[] = [];

  constructor(private transferService: TransferService) {}

  ngOnInit() {
    this.loadStations();
  }

  loadStations() {
    this.transferService.getStations().subscribe(
      (data) => {
        this.stations = data;
        this.setupFilteredStations();
      },
      (error) => console.error('Error loading stations', error)
    );
  }

  setupFilteredStations() {
    this.filteredStations = this.stationControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value || ''))
    );
  }

  private _filter(value: string): Station[] {
    const filterValue = value.toLowerCase();
    return this.stations.filter(station => station.name.toLowerCase().includes(filterValue));
  }

  displayFn(station: Station): string {
    return station && station.name ? station.name : '';
  }

  onSubmit() {
    const selectedStation = this.stationControl.value;
    if (selectedStation && this.fromTrack && this.toTrack) {
      console.warn(selectedStation)
      // @ts-ignore
      this.transferService.getInstructions(selectedStation['id'], this.fromTrack, this.toTrack).subscribe(
        (data) => {
          this.instructions = data;
        },
        (error) => console.error('Error getting instructions', error)
      );
    }
  }
}
