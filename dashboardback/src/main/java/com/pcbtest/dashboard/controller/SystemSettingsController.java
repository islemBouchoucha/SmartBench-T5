package com.pcbtest.dashboard.controller;

import com.pcbtest.dashboard.dto.SystemSettingsDtos.SystemSettingsResponse;
import com.pcbtest.dashboard.service.SystemSettingsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
@RequiredArgsConstructor
public class SystemSettingsController {

    private final SystemSettingsService settingsService;

    @GetMapping
    public ResponseEntity<SystemSettingsResponse> getSettings() {
        return ResponseEntity.ok(settingsService.getSettings());
    }

    @PutMapping
    public ResponseEntity<SystemSettingsResponse> saveSettings(@Valid @RequestBody SystemSettingsResponse request) {
        return ResponseEntity.ok(settingsService.saveSettings(request));
    }
}
