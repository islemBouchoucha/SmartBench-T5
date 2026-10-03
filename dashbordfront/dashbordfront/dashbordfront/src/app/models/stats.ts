export interface ElectricalStat {
  avg: number;
  min: number;
  max: number;
}

export interface SummaryStats {
  totalTests: number;
  passCount: number;
  failCount: number;
  blockedCount: number;
  passRate: number;
  defectBreakdown: { [key: string]: number };

  // Agrégats électriques optionnels (à ajouter côté backend si besoin).
  // Si absents, le dashboard calcule une approximation à partir des tests
  // actuellement chargés (page courante).
  voltageStats?: ElectricalStat;
  currentStats?: ElectricalStat;
  resistanceStats?: ElectricalStat;
  powerStats?: ElectricalStat;
  temperatureStats?: ElectricalStat;
}

export interface TrendPoint {
  date: string;
  pass: number;
  fail: number;
  blocked: number;
}

export interface TrendStats {
  points: TrendPoint[];
}