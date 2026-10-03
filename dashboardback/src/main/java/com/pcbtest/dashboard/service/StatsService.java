package com.pcbtest.dashboard.service;

import com.pcbtest.dashboard.dto.StatsDtos.SummaryStats;
import com.pcbtest.dashboard.dto.StatsDtos.TrendPoint;
import com.pcbtest.dashboard.dto.StatsDtos.TrendStats;
import com.pcbtest.dashboard.repository.PcbTestRepository;
import com.pcbtest.dashboard.repository.VisualResultRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class StatsService {

    private final PcbTestRepository pcbTestRepository;
    private final VisualResultRepository visualResultRepository;

    public SummaryStats getSummary() {
        long total = pcbTestRepository.count();
        long pass = pcbTestRepository.countByOverallStatus("PASS");
        long fail = pcbTestRepository.countByOverallStatus("FAIL");
        long blocked = pcbTestRepository.countByOverallStatus("BLOCKED");
        double passRate = total == 0 ? 0.0 : Math.round((pass * 10000.0 / total)) / 100.0;

        Map<String, Long> defects = new LinkedHashMap<>();
        defects.put("Composants manquants", nz(visualResultRepository.sumMissingComponents()));
        defects.put("Composants mal placés", nz(visualResultRepository.sumMisplacedComponents()));
        defects.put("Défauts de soudure", nz(visualResultRepository.sumSolderDefects()));
        defects.put("Connecteurs endommagés", nz(visualResultRepository.sumDamagedConnectors()));

        return new SummaryStats(total, pass, fail, blocked, passRate, defects);
    }

    public TrendStats getTrend(int days) {
        LocalDateTime from = LocalDateTime.now().minusDays(days);
        List<Object[]> rows = pcbTestRepository.countTestsByDayAndStatus(from);

        Map<String, long[]> byDay = new LinkedHashMap<>(); // [pass, fail, blocked]

        for (Object[] row : rows) {
            String day = row[0].toString();
            String status = (String) row[1];
            long count = ((Number) row[2]).longValue();

            long[] counts = byDay.computeIfAbsent(day, k -> new long[3]);
            switch (status) {
                case "PASS" -> counts[0] += count;
                case "FAIL" -> counts[1] += count;
                case "BLOCKED" -> counts[2] += count;
                default -> {}
            }
        }

        List<TrendPoint> points = byDay.entrySet().stream()
                .map(entry -> new TrendPoint(entry.getKey(), entry.getValue()[0], entry.getValue()[1], entry.getValue()[2]))
                .toList();

        return new TrendStats(points);
    }

    private long nz(Long value) {
        return value == null ? 0L : value;
    }
}
