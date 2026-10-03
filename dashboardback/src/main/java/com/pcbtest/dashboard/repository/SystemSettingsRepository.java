package com.pcbtest.dashboard.repository;

import com.pcbtest.dashboard.entity.SystemSettings;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SystemSettingsRepository extends JpaRepository<SystemSettings, Long> {
}
