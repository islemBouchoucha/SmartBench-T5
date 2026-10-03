package com.pcbtest.dashboard.dto;

import java.util.List;
import java.util.Map;

public class StatsDtos {

    public record SummaryStats(
            long totalTests,
            long passCount,
            long failCount,
            long blockedCount,
            double passRate, // en pourcentage
            Map<String, Long> defectBreakdown // ex: {"composants manquants": 12, "soudure": 5, ...}
    ) {}

    public record TrendPoint(
            String date,
            long pass,
            long fail,
            long blocked
    ) {}

    public record TrendStats(
            List<TrendPoint> points
    ) {}
}
