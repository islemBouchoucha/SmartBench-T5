import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  ChangePasswordRequest,
  UpdateProfileRequest,
  User,
  UserCreateRequest,
  UserUpdateRequest
} from '../models/user';
import { PageResponse, PcbTestSummary } from '../models/pcb-test';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private baseUrl = 'http://localhost:9090/api/users';

  constructor(private http: HttpClient) {}

  // --- Gestion des utilisateurs (page Utilisateurs, réservée ADMIN) ---

  listUsers(search?: string): Observable<User[]> {
    const params: any = {};
    if (search) params.search = search;
    return this.http.get<User[]>(this.baseUrl, { params });
  }

  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${id}`);
  }

  createUser(request: UserCreateRequest): Observable<User> {
    return this.http.post<User>(this.baseUrl, request);
  }

  updateUser(id: number, request: UserUpdateRequest): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/${id}`, request);
  }

  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  setActive(id: number, active: boolean): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/${id}/status`, { active });
  }

  // --- Profil du compte connecté ---

  getMyProfile(): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/me`);
  }

  updateMyProfile(request: UpdateProfileRequest): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/me`, request);
  }

  changePassword(request: ChangePasswordRequest): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/me/password`, request);
  }

  // Historique d'activité : réutilise l'endpoint des tests filtré par opérateur,
  // en attendant un éventuel endpoint dédié côté backend.
  getMyActivity(username: string, page: number = 0, size: number = 10): Observable<PageResponse<PcbTestSummary>> {
    return this.http.get<PageResponse<PcbTestSummary>>('http://localhost:9090/api/tests', {
      params: { page: page.toString(), size: size.toString(), search: username }
    });
  }
}
