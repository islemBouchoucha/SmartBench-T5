import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse, PcbTestSummary } from '../models/pcb-test';

@Injectable({
  providedIn: 'root'
})
export class PcbTest {
  private baseUrl = 'http://localhost:9090/api/tests';

  constructor(private http: HttpClient) {}

  listTests(page: number = 0, size: number = 10, status?: string, search?: string): Observable<PageResponse<PcbTestSummary>> {
    let params: any = { page: page.toString(), size: size.toString() };
    if (status) params.status = status;
    if (search) params.search = search;

    return this.http.get<PageResponse<PcbTestSummary>>(this.baseUrl, { params });
  }
}