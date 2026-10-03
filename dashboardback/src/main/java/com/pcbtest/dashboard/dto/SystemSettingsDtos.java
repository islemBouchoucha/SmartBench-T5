package com.pcbtest.dashboard.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

public class SystemSettingsDtos {

    public record SystemSettingsResponse(
            @Min(0) @Max(100) double failRateAlertThreshold,
            @Min(0) @Max(100) double blockedAlertThreshold,
            boolean emailNotifications,
            @Min(5) int dashboardAutoRefreshSeconds
    ) {}
}
