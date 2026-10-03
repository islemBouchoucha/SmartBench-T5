export interface DisplayPreferences {
  theme: 'light' | 'dark';
  language: 'fr' | 'en';
}

export interface SystemSettings {
  failRateAlertThreshold: number;
  blockedAlertThreshold: number;
  emailNotifications: boolean;
  dashboardAutoRefreshSeconds: number;
}
