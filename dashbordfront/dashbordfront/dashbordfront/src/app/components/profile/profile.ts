import { ChangeDetectorRef, Component, OnInit, PLATFORM_ID, inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { Sidebar } from '../sidebar/sidebar';
import { UserService } from '../../services/user';
import { User } from '../../models/user';
import { PcbTestSummary } from '../../models/pcb-test';
import { TranslatePipe } from '../../pipes/translate';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, Sidebar, TranslatePipe],
  templateUrl: './profile.html',
  styleUrl: './profile.css'
})
export class Profile implements OnInit {
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  isLoading = true;
  errorMessage = '';
  successMessage = '';

  user: User | null = null;
  isEditingInfo = false;
  isSavingInfo = false;
  infoError = '';
  infoForm = { fullName: '', email: '' };

  isChangingPassword = false;
  isSavingPassword = false;
  passwordError = '';
  passwordSuccess = '';
  passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };

  activity: PcbTestSummary[] = [];
  isLoadingActivity = true;

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      this.isLoading = false;
      return;
    }
    this.loadProfile();
  }

  loadProfile(): void {
    this.isLoading = true;
    this.errorMessage = '';
    this.userService
      .getMyProfile()
      .pipe(finalize(() => {
        this.isLoading = false;
        this.cdr.markForCheck();
      }))
      .subscribe({
        next: (user) => {
          this.user = user;
          this.infoForm = { fullName: user.fullName, email: user.email };
          this.loadActivity(user.username);
          this.cdr.markForCheck();
        },
        error: (err) => {
          console.error('Erreur GET /api/users/me :', err);
          if (err?.status === 0) {
            this.errorMessage = "Impossible de joindre le serveur (backend éteint ou CORS bloqué).";
          } else if (err?.status === 404) {
            this.errorMessage = "L'endpoint /api/users/me n'existe pas encore côté backend.";
          } else if (err?.status === 401 || err?.status === 403) {
            this.errorMessage = 'Session expirée. Veuillez vous reconnecter.';
          } else {
            this.errorMessage = `Impossible de charger votre profil (erreur ${err?.status ?? '?'}).`;
          }
          this.cdr.markForCheck();
        }
      });
  }

  loadActivity(username: string): void {
    this.isLoadingActivity = true;
    this.userService.getMyActivity(username).subscribe({
      next: (page) => {
        this.activity = page.content ?? [];
        this.isLoadingActivity = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.isLoadingActivity = false;
        this.cdr.markForCheck();
      }
    });
  }

  startEditInfo(): void {
    if (!this.user) return;
    this.infoForm = { fullName: this.user.fullName, email: this.user.email };
    this.infoError = '';
    this.isEditingInfo = true;
  }

  cancelEditInfo(): void {
    this.isEditingInfo = false;
  }

  saveInfo(): void {
    if (!this.infoForm.fullName || !this.infoForm.email) {
      this.infoError = 'Veuillez remplir tous les champs.';
      return;
    }
    this.isSavingInfo = true;
    this.infoError = '';
    this.userService.updateMyProfile(this.infoForm).subscribe({
      next: (user) => {
        this.user = user;
        this.isEditingInfo = false;
        this.isSavingInfo = false;
        this.successMessage = 'Informations mises à jour.';
        this.cdr.markForCheck();
        setTimeout(() => {
          this.successMessage = '';
          this.cdr.markForCheck();
        }, 4000);
      },
      error: () => {
        this.isSavingInfo = false;
        this.infoError = 'Erreur lors de la mise à jour.';
        this.cdr.markForCheck();
      }
    });
  }

  openPasswordForm(): void {
    this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
    this.passwordError = '';
    this.passwordSuccess = '';
    this.isChangingPassword = true;
  }

  cancelPasswordForm(): void {
    this.isChangingPassword = false;
  }

  submitPasswordChange(): void {
    this.passwordError = '';

    if (!this.passwordForm.currentPassword || !this.passwordForm.newPassword) {
      this.passwordError = 'Veuillez remplir tous les champs.';
      return;
    }
    if (this.passwordForm.newPassword.length < 8) {
      this.passwordError = 'Le nouveau mot de passe doit contenir au moins 8 caractères.';
      return;
    }
    if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
      this.passwordError = 'La confirmation ne correspond pas au nouveau mot de passe.';
      return;
    }

    this.isSavingPassword = true;
    this.userService
      .changePassword({
        currentPassword: this.passwordForm.currentPassword,
        newPassword: this.passwordForm.newPassword
      })
      .subscribe({
        next: () => {
          this.isSavingPassword = false;
          this.passwordSuccess = 'Mot de passe modifié avec succès.';
          this.passwordForm = { currentPassword: '', newPassword: '', confirmPassword: '' };
          this.cdr.markForCheck();
          setTimeout(() => {
            this.isChangingPassword = false;
            this.passwordSuccess = '';
            this.cdr.markForCheck();
          }, 2000);
        },
        error: (err) => {
          this.isSavingPassword = false;
          this.passwordError =
            err?.status === 401 || err?.status === 403
              ? 'Mot de passe actuel incorrect.'
              : 'Erreur lors du changement de mot de passe.';
          this.cdr.markForCheck();
        }
      });
  }

  statusClass(status: string): string {
    switch (status?.toUpperCase()) {
      case 'PASS': return 'badge badge-pass';
      case 'FAIL': return 'badge badge-fail';
      case 'BLOCKED': return 'badge badge-blocked';
      default: return 'badge';
    }
  }
}