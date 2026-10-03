import { ChangeDetectorRef, Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Sidebar } from '../sidebar/sidebar';
import { UserService } from '../../services/user';
import { ROLES, User, UserCreateRequest, UserUpdateRequest } from '../../models/user';
import { TranslatePipe } from '../../pipes/translate';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, FormsModule, Sidebar, TranslatePipe],
  templateUrl: './users.html',
  styleUrl: './users.css'
})
export class Users implements OnInit {
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  roles = ROLES;
  users: User[] = [];
  isLoading = true;
  errorMessage = '';
  successMessage = '';

  searchTerm = '';

  // Modal state
  isModalOpen = false;
  isEditMode = false;
  isSaving = false;
  formError = '';
  selectedUser: User | null = null;

  form: { username: string; fullName: string; email: string; role: string; password: string; active: boolean } = {
    username: '',
    fullName: '',
    email: '',
    role: 'OPERATEUR',
    password: '',
    active: true
  };

  // Delete confirmation
  userPendingDelete: User | null = null;

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.loadUsers();
    } else {
      this.isLoading = false;
    }
  }

  loadUsers(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.userService.listUsers(this.searchTerm || undefined).subscribe({
      next: (data) => {
        this.users = data;
        this.isLoading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.handleError(err, 'Impossible de charger la liste des utilisateurs.');
        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }

  onSearch(): void {
    this.loadUsers();
  }

  openCreateModal(): void {
    this.isEditMode = false;
    this.selectedUser = null;
    this.formError = '';
    this.form = { username: '', fullName: '', email: '', role: 'OPERATEUR', password: '', active: true };
    this.isModalOpen = true;
  }

  openEditModal(user: User): void {
    this.isEditMode = true;
    this.selectedUser = user;
    this.formError = '';
    this.form = {
      username: user.username,
      fullName: user.fullName,
      email: user.email,
      role: user.role,
      password: '',
      active: user.active
    };
    this.isModalOpen = true;
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  submitForm(): void {
    this.formError = '';

    if (!this.form.fullName || !this.form.email || !this.form.role) {
      this.formError = 'Veuillez remplir tous les champs obligatoires.';
      return;
    }

    if (!this.isEditMode && (!this.form.username || !this.form.password)) {
      this.formError = "Nom d'utilisateur et mot de passe sont requis pour créer un compte.";
      return;
    }

    this.isSaving = true;

    if (this.isEditMode && this.selectedUser) {
      const payload: UserUpdateRequest = {
        fullName: this.form.fullName,
        email: this.form.email,
        role: this.form.role,
        active: this.form.active
      };
      this.userService.updateUser(this.selectedUser.id, payload).subscribe({
        next: () => this.onSaveSuccess('Utilisateur modifié avec succès.'),
        error: (err) => this.onSaveError(err)
      });
    } else {
      const payload: UserCreateRequest = {
        username: this.form.username,
        fullName: this.form.fullName,
        email: this.form.email,
        role: this.form.role,
        password: this.form.password
      };
      this.userService.createUser(payload).subscribe({
        next: () => this.onSaveSuccess('Utilisateur créé avec succès.'),
        error: (err) => this.onSaveError(err)
      });
    }
  }

  private onSaveSuccess(message: string): void {
    this.isSaving = false;
    this.isModalOpen = false;
    this.successMessage = message;
    this.loadUsers();
    this.cdr.markForCheck();
    setTimeout(() => {
      this.successMessage = '';
      this.cdr.markForCheck();
    }, 4000);
  }

  private onSaveError(err: HttpErrorResponse): void {
    this.isSaving = false;
    if (err.status === 409) {
      this.formError = "Ce nom d'utilisateur ou cet email existe déjà.";
    } else if (err.status === 401 || err.status === 403) {
      this.formError = "Vous n'avez pas les droits nécessaires pour cette action.";
    } else {
      this.formError = "Erreur lors de l'enregistrement.";
    }
    this.cdr.markForCheck();
  }

  toggleActive(user: User): void {
    this.userService.setActive(user.id, !user.active).subscribe({
      next: (updated) => {
        user.active = updated.active;
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.handleError(err, "Impossible de modifier le statut de l'utilisateur.");
        this.cdr.markForCheck();
      }
    });
  }

  askDelete(user: User): void {
    this.userPendingDelete = user;
  }

  cancelDelete(): void {
    this.userPendingDelete = null;
  }

  confirmDelete(): void {
    if (!this.userPendingDelete) return;
    const id = this.userPendingDelete.id;
    this.userService.deleteUser(id).subscribe({
      next: () => {
        this.users = this.users.filter((u) => u.id !== id);
        this.userPendingDelete = null;
        this.successMessage = 'Utilisateur supprimé.';
        this.cdr.markForCheck();
        setTimeout(() => {
          this.successMessage = '';
          this.cdr.markForCheck();
        }, 4000);
      },
      error: (err) => {
        this.handleError(err, 'Impossible de supprimer cet utilisateur.');
        this.userPendingDelete = null;
        this.cdr.markForCheck();
      }
    });
  }

  private handleError(err: any, fallbackMessage: string): void {
    if (err?.status === 401 || err?.status === 403) {
      this.errorMessage = 'Session expirée ou non autorisée. Veuillez vous reconnecter.';
    } else {
      this.errorMessage = fallbackMessage;
    }
  }

  roleClass(role: string): string {
    switch (role?.toUpperCase()) {
      case 'ADMIN': return 'badge badge-admin';
      case 'OPERATEUR': return 'badge badge-operateur';
      case 'TECHNICIEN': return 'badge badge-technicien';
      default: return 'badge';
    }
  }
}