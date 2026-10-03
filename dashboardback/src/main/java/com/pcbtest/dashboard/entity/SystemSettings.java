package com.pcbtest.dashboard.entity;

import jakarta.persistence.*;
import lombok.*;

// Table à une seule ligne (id fixe = 1) : réglages globaux de supervision.
@Entity
@Table(name = "system_settings")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SystemSettings {

    @Id
    private Long id;

    @Column(name = "fail_rate_alert_threshold", nullable = false)
    private double failRateAlertThreshold;

    @Column(name = "blocked_alert_threshold", nullable = false)
    private double blockedAlertThreshold;

    @Column(name = "email_notifications", nullable = false)
    private boolean emailNotifications;

    @Column(name = "dashboard_auto_refresh_seconds", nullable = false)
    private int dashboardAutoRefreshSeconds;
}
