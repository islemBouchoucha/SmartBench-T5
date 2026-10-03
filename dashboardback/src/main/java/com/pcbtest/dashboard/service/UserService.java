package com.pcbtest.dashboard.service;

import com.pcbtest.dashboard.dto.UserDtos.*;
import com.pcbtest.dashboard.entity.User;
import com.pcbtest.dashboard.exception.ResourceNotFoundException;
import com.pcbtest.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // --- Gestion des utilisateurs (réservé ROLE_ADMIN, cf. SecurityConfig) ---

    public List<UserResponse> listUsers(String search) {
        List<User> users = StringUtils.hasText(search)
                ? userRepository.findByUsernameContainingIgnoreCaseOrFullNameContainingIgnoreCase(search, search)
                : userRepository.findAll();
        return users.stream().map(this::toResponse).toList();
    }

    public UserResponse getUser(Long id) {
        return toResponse(findByIdOrThrow(id));
    }

    @Transactional
    public UserResponse createUser(UserCreateRequest request) {
        if (userRepository.existsByUsername(request.username())) {
            throw new IllegalArgumentException("Ce nom d'utilisateur existe déjà");
        }
        User user = User.builder()
                .username(request.username())
                .fullName(request.fullName())
                .email(request.email())
                .role(request.role())
                .password(passwordEncoder.encode(request.password()))
                .active(true)
                .build();
        return toResponse(userRepository.save(user));
    }

    @Transactional
    public UserResponse updateUser(Long id, UserUpdateRequest request) {
        User user = findByIdOrThrow(id);
        user.setFullName(request.fullName());
        user.setEmail(request.email());
        user.setRole(request.role());
        user.setActive(request.active());
        return toResponse(userRepository.save(user));
    }

    @Transactional
    public UserResponse setActive(Long id, boolean active) {
        User user = findByIdOrThrow(id);
        user.setActive(active);
        return toResponse(userRepository.save(user));
    }

    @Transactional
    public void deleteUser(Long id) {
        User user = findByIdOrThrow(id);
        userRepository.delete(user);
    }

    // --- Profil du compte connecté ---

    public UserResponse getMyProfile(String username) {
        return toResponse(findByUsernameOrThrow(username));
    }

    @Transactional
    public UserResponse updateMyProfile(String username, UpdateProfileRequest request) {
        User user = findByUsernameOrThrow(username);
        user.setFullName(request.fullName());
        user.setEmail(request.email());
        return toResponse(userRepository.save(user));
    }

    @Transactional
    public void changePassword(String username, ChangePasswordRequest request) {
        User user = findByUsernameOrThrow(username);
        if (!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new BadCredentialsException("Mot de passe actuel incorrect");
        }
        user.setPassword(passwordEncoder.encode(request.newPassword()));
        userRepository.save(user);
    }

    // --- Helpers ---

    private User findByIdOrThrow(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Utilisateur introuvable, id=" + id));
    }

    private User findByUsernameOrThrow(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("Utilisateur introuvable : " + username));
    }

    private UserResponse toResponse(User user) {
        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getFullName(),
                user.getEmail(),
                user.getRole(),
                user.isActive(),
                user.getCreatedAt(),
                user.getLastLogin()
        );
    }
}
