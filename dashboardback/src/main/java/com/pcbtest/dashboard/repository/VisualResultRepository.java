package com.pcbtest.dashboard.repository;

import com.pcbtest.dashboard.entity.VisualResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface VisualResultRepository extends JpaRepository<VisualResult, Long> {

    @Query("SELECT SUM(v.missingComponentsCount) FROM VisualResult v")
    Long sumMissingComponents();

    @Query("SELECT SUM(v.misplacedComponentsCount) FROM VisualResult v")
    Long sumMisplacedComponents();

    @Query("SELECT SUM(v.solderDefectsCount) FROM VisualResult v")
    Long sumSolderDefects();

    @Query("SELECT SUM(v.damagedConnectorsCount) FROM VisualResult v")
    Long sumDamagedConnectors();
}
