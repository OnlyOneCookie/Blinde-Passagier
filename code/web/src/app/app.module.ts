import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {NgModule} from "@angular/core";
import {SbbButton} from "@sbb-esta/angular/button";
import {SbbInput} from "@sbb-esta/angular/input";
import {SbbSelect} from "@sbb-esta/angular/select";
import {SbbIcon} from "@sbb-esta/angular/icon";
import {FormsModule} from "@angular/forms";

@NgModule({
    imports: [
      BrowserAnimationsModule,
      FormsModule,
      SbbButton,
      SbbInput,
      SbbSelect,
      SbbIcon
    ],
  providers: []
})
export class AppModule {}
