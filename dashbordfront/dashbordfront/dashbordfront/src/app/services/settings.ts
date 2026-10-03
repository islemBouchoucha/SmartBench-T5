import { Injectable, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { DisplayPreferences, SystemSettings } from '../models/settings';
import { TranslationService } from './translation';

const PREFS_KEY = 'display-preferences';

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private baseUrl = 'http://localhost:9090/api/settings';
  private platformId = inject(PLATFORM_ID);
  private translationService = inject(TranslationService);

  private defaultPrefs: DisplayPreferences = { theme: 'light', language: 'fr' };

  constructor(private http: HttpClient) {}

  // --- Préférences d'affichage : stockées côté client (pas besoin de backend) ---

  getDisplayPreferences(): DisplayPreferences {
    if (!isPlatformBrowser(this.platformId)) return this.defaultPrefs;
    const raw = localStorage.getItem(PREFS_KEY);
    return raw ? JSON.parse(raw) : this.defaultPrefs;
  }

  saveDisplayPreferences(prefs: DisplayPreferences): void {
    if (!isPlatformBrowser(this.platformId)) return;
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    document.documentElement.setAttribute('data-theme', prefs.theme);
    this.translationService.setLanguage(prefs.language);
  }

  applyStoredTheme(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    const prefs = this.getDisplayPreferences();
    document.documentElement.setAttribute('data-theme', prefs.theme);
    this.translationService.setLanguage(prefs.language);
  }

  // --- Paramètres système : nécessitent un endpoint backend GET/PUT /api/settings ---
  // NB : à ajouter côté Spring Boot si l'endpoint n'existe pas encore.

  getSystemSettings(): Observable<SystemSettings> {
    return this.http.get<SystemSettings>(this.baseUrl);
  }

  saveSystemSettings(settings: SystemSettings): Observable<SystemSettings> {
    return this.http.put<SystemSettings>(this.baseUrl, settings);
  }
}
