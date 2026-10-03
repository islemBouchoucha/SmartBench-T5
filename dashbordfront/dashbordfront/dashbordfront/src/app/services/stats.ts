import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SummaryStats, TrendStats } from '../models/stats';

@Injectable({
  providedIn: 'root'
})
export class Stats {
  private baseUrl = 'http://localhost:9090/api/stats';

  constructor(private http: HttpClient) {}

  getSummary(): Observable<SummaryStats> {
    return this.http.get<SummaryStats>(`${this.baseUrl}/summary`);
  }

  getTrend(days: number = 14): Observable<TrendStats> {
    return this.http.get<TrendStats>(`${this.baseUrl}/trend`, {
      params: { days: days.toString() }
    });
  }
}