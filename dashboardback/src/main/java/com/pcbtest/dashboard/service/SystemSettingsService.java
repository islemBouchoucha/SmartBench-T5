package com.pcbtest.dashboard.service;

import com.pcbtest.dashboard.dto.SystemSettingsDtos.SystemSettingsResponse;
import com.pcbtest.dashboard.entity.SystemSettings;
import com.pcbtest.dashboard.repository.SystemSettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class SystemSettingsService {

    private static final Long SINGLETON_ID = 1L;

    private final SystemSettingsRepository repository;

    public SystemSettingsResponse getSettings() {
        return toResponse(getOrCreateDefault());
    }

    @Transactional
    public SystemSettingsResponse saveSettings(SystemSettingsResponse request) {
        SystemSettings settings = getOrCreateDefault();
        settings.setFailRateAlertThreshold(request.failRateAlertThreshold());
        settings.setBlockedAlertThreshold(request.blockedAlertThreshold());
        settings.setEmailNotifications(request.emailNotifications());
        settings.setDashboardAutoRefreshSeconds(request.dashboardAutoRefreshSeconds());
        return toResponse(repository.save(settings));
    }

    private SystemSettings getOrCreateDefault() {
        return repository.findById(SINGLETON_ID).orElseGet(() -> repository.save(
                SystemSettings.builder()
                        .id(SINGLETON_ID)
                        .failRateAlertThreshold(10)
                        .blockedAlertThreshold(5)
                        .emailNotifications(true)
                        .dashboardAutoRefreshSeconds(30)
                        .build()
        ));
    }

    private SystemSettingsResponse toResponse(SystemSettings s) {
        return new SystemSettingsResponse(
                s.getFailRateAlertThreshold(),
                s.getBlockedAlertThreshold(),
                s.isEmailNotifications(),
                s.getDashboardAutoRefreshSeconds()
        );
    }
}
