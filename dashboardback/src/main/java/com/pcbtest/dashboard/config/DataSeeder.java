package com.pcbtest.dashboard.config;

import com.pcbtest.dashboard.entity.User;
import com.pcbtest.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Crée un compte qualité par défaut au premier démarrage, uniquement si la table users est vide.
 * Identifiants : admin / admin123 — à changer immédiatement après le premier login.
 */
@Component
@RequiredArgsConstructor
public class DataSeeder implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (userRepository.count() == 0) {
            User qualite = User.builder()
                    .username("admin")
                    .fullName("Administrateur Qualité")
                    .email("admin@sagemcom.local")
                    .password(passwordEncoder.encode("admin123"))
                    .role("ROLE_QUALITE")
                    .active(true)
                    .build();
            userRepository.save(qualite);

            User admin = User.builder()
                    .username("superadmin")
                    .fullName("Super Administrateur")
                    .email("superadmin@sagemcom.local")
                    .password(passwordEncoder.encode("admin123"))
                    .role("ROLE_ADMIN")
                    .active(true)
                    .build();
            userRepository.save(admin);

            System.out.println("=> Comptes par défaut créés : admin / admin123 (ROLE_QUALITE) et superadmin / admin123 (ROLE_ADMIN) — changez ces mots de passe !");
        }
    }
}
