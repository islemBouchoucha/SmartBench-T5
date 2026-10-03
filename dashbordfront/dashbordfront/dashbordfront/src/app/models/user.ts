export interface User {
  id: number;
  username: string;
  fullName: string;
  email: string;
  role: string;
  active: boolean;
  createdAt?: string;
  lastLogin?: string;
}

export interface UserCreateRequest {
  username: string;
  fullName: string;
  email: string;
  role: string;
  password: string;
}

export interface UserUpdateRequest {
  fullName: string;
  email: string;
  role: string;
  active: boolean;
}

export interface UpdateProfileRequest {
  fullName: string;
  email: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

export const ROLES = ['ADMIN', 'OPERATEUR', 'TECHNICIEN'];
