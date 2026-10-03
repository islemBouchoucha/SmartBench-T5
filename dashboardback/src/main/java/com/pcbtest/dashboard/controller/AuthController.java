package com.pcbtest.dashboard.controller;

import com.pcbtest.dashboard.dto.AuthDtos.LoginRequest;
import com.pcbtest.dashboard.dto.AuthDtos.LoginResponse;
import com.pcbtest.dashboard.dto.AuthDtos.RegisterRequest;
import com.pcbtest.dashboard.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    // Endpoint pratique pour créer les premiers comptes (opérateur / qualité) en phase de démarrage.
    // A restreindre (ex: réservé à ROLE_ADMIN) ou retirer une fois les comptes de base créés.
    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        authService.register(request);
        return ResponseEntity.ok().build();
    }
}
