import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SettingsService } from './services/settings';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  protected readonly title = signal('dashbordfront');

  constructor(private settingsService: SettingsService) {}

  ngOnInit(): void {
    // Réapplique le thème sombre/clair enregistré à chaque chargement/rafraîchissement de l'app.
    this.settingsService.applyStoredTheme();
  }
}
