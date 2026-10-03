import { ChangeDetectorRef, Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { Sidebar } from '../sidebar/sidebar';
import { SettingsService } from '../../services/settings';
import { DisplayPreferences, SystemSettings } from '../../models/settings';
import { TranslatePipe } from '../../pipes/translate';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, Sidebar, TranslatePipe],
  templateUrl: './settings.html',
  styleUrl: './settings.css'
})
export class Settings implements OnInit {
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  prefs: DisplayPreferences = { theme: 'light', language: 'fr' };
  prefsSaved = false;

  system: SystemSettings = {
    failRateAlertThreshold: 10,
    blockedAlertThreshold: 5,
    emailNotifications: true,
    dashboardAutoRefreshSeconds: 30
  };
  isLoadingSystem = true;
  isSavingSystem = false;
  systemError = '';
  systemSaved = false;

  constructor(private settingsService: SettingsService) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      this.isLoadingSystem = false;
      return;
    }

    this.prefs = this.settingsService.getDisplayPreferences();
    this.loadSystemSettings();
  }

  // --- Préférences d'affichage ---

  savePreferences(): void {
    this.settingsService.saveDisplayPreferences(this.prefs);
    this.prefsSaved = true;
    setTimeout(() => {
      this.prefsSaved = false;
      this.cdr.markForCheck();
    }, 3000);
  }

  // --- Paramètres système ---

  loadSystemSettings(): void {
    this.isLoadingSystem = true;
    this.systemError = '';
    this.settingsService
      .getSystemSettings()
      .pipe(finalize(() => {
        this.isLoadingSystem = false;
        this.cdr.markForCheck();
      }))
      .subscribe({
        next: (data) => {
          this.system = data;
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Erreur GET /api/settings :', err);
          // Endpoint pas encore disponible côté backend, ou droits insuffisants (réservé ROLE_ADMIN) :
          // on garde les valeurs par défaut, sans bloquer l'écran.
          this.cdr.markForCheck();
        }
      });
  }

  saveSystemSettings(): void {
    this.isSavingSystem = true;
    this.systemError = '';
    this.settingsService.saveSystemSettings(this.system).subscribe({
      next: () => {
        this.isSavingSystem = false;
        this.systemSaved = true;
        this.cdr.markForCheck();
        setTimeout(() => {
          this.systemSaved = false;
          this.cdr.markForCheck();
        }, 3000);
      },
      error: () => {
        this.isSavingSystem = false;
        this.systemError = "Impossible d'enregistrer : l'endpoint /api/settings n'est pas encore implémenté côté backend.";
        this.cdr.markForCheck();
      }
    });
  }
}