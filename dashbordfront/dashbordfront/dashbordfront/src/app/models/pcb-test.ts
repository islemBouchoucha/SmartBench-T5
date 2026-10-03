export interface PcbTestSummary {
  id: number;
  serialNumber: string;
  testDate: string;
  overallStatus: string;
  operatorUsername: string;
  visualStatus: string;
  electricalStatus: string;

  // Paramètres électriques mesurés (optionnels : le dashboard les affiche
  // uniquement si le backend les renvoie. À confirmer/renommer avec l'API réelle).
  voltage?: number;      // Tension (V)
  current?: number;      // Courant (A)
  resistance?: number;   // Résistance (Ω)
  power?: number;        // Puissance (W)
  temperature?: number;  // Température (°C)
}

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
  size: number;
}