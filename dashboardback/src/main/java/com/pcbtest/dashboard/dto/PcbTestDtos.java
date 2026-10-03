package com.pcbtest.dashboard.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public class PcbTestDtos {

    // Résumé utilisé dans la liste / tableau du dashboard
    public record PcbTestSummary(
            Long id,
            String serialNumber,
            LocalDateTime testDate,
            String overallStatus,
            String operatorUsername,
            String visualStatus,
            String electricalStatus
    ) {}

    // Détail complet d'une carte (dossier complet demandé dans le cahier des charges)
    public record PcbTestDetail(
            Long id,
            String serialNumber,
            LocalDateTime testDate,
            String overallStatus,
            String operatorUsername,
            VisualResultDto visualResult,
            ElectricalResultDto electricalResult
    ) {}

    public record VisualResultDto(
            String imagePath,
            Integer missingComponentsCount,
            Integer misplacedComponentsCount,
            Integer solderDefectsCount,
            Integer damagedConnectorsCount,
            Boolean isBlockingAnomaly,
            BigDecimal aiConfidenceScore,
            String visualStatus
    ) {}

    public record ElectricalResultDto(
            BigDecimal tension,
            BigDecimal courant,
            BigDecimal gainMes1,
            BigDecimal gainMes2,
            BigDecimal gainMes3,
            BigDecimal puissance,
            BigDecimal rms,
            BigDecimal temperature,
            String classicStatus,
            BigDecimal aiAnomalyScore,
            String aiStatus
    ) {}

    // Payload envoyé par le banc de test / Raspberry Pi pour créer un nouveau test
    public record CreatePcbTestRequest(
            @NotBlank String serialNumber,
            Long operatorId,
            VisualResultDto visualResult,
            ElectricalResultDto electricalResult
    ) {}
}
