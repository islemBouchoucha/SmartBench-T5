package com.pcbtest.dashboard.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;

public class UserDtos {

    public record UserResponse(
            Long id,
            String username,
            String fullName,
            String email,
            String role,
            boolean active,
            LocalDateTime createdAt,
            LocalDateTime lastLogin
    ) {}

    public record UserCreateRequest(
            @NotBlank String username,
            @NotBlank String fullName,
            @Email String email,
            @NotBlank String role,
            @NotBlank @Size(min = 6, message = "doit contenir au moins 6 caractères") String password
    ) {}

    public record UserUpdateRequest(
            @NotBlank String fullName,
            @Email String email,
            @NotBlank String role,
            boolean active
    ) {}

    public record UpdateProfileRequest(
            @NotBlank String fullName,
            @Email String email
    ) {}

    public record ChangePasswordRequest(
            @NotBlank String currentPassword,
            @NotBlank @Size(min = 6, message = "doit contenir au moins 6 caractères") String newPassword
    ) {}

    public record UpdateStatusRequest(
            boolean active
    ) {}
}
