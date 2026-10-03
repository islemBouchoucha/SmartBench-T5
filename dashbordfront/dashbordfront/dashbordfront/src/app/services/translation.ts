import { Injectable, PLATFORM_ID, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Lang, TRANSLATIONS } from '../i18n/translations';

const PREFS_KEY = 'display-preferences';

@Injectable({
  providedIn: 'root'
})
export class TranslationService {
  private platformId = inject(PLATFORM_ID);

  // Signal réactif : tous les composants utilisant le pipe "translate" se
  // mettent à jour automatiquement dès que la langue change, sans reload.
  readonly currentLang = signal<Lang>('fr');

  constructor() {
    if (isPlatformBrowser(this.platformId)) {
      const raw = localStorage.getItem(PREFS_KEY);
      if (raw) {
        try {
          const prefs = JSON.parse(raw);
          if (prefs.language === 'en' || prefs.language === 'fr') {
            this.currentLang.set(prefs.language);
          }
        } catch {
          // valeur corrompue -> on garde le défaut 'fr'
        }
      }
    }
  }

  setLanguage(lang: Lang): void {
    this.currentLang.set(lang);
  }

  translate(key: string): string {
    const dict = TRANSLATIONS[this.currentLang()];
    return dict[key] ?? key;
  }
}
