import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth';
import { TranslatePipe } from '../../pipes/translate';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslatePipe],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {

  username = '';
  password = '';
  errorMessage = '';
  isLoading = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {

    if (!this.username || !this.password) {
      this.errorMessage = 'Veuillez remplir tous les champs.';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login({
      username: this.username,
      password: this.password
    }).subscribe({

      next: () => {
        this.isLoading = false;
        this.router.navigate(['/dashboard']);
      },

      error: (err: HttpErrorResponse) => {

        this.isLoading = false;

        console.log(err);
        alert("Erreur détectée");

        if (err.status === 401) {
          this.errorMessage = "Nom d'utilisateur ou mot de passe incorrect.";
        } else if (err.status === 0) {
          this.errorMessage = "Impossible de contacter le serveur.";
        } else {
          this.errorMessage = "Erreur : " + err.status;
        }
      }

    });

  }
}