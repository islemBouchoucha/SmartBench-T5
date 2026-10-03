package com.pcbtest.dashboard.controller;

import com.pcbtest.dashboard.dto.StatsDtos.SummaryStats;
import com.pcbtest.dashboard.dto.StatsDtos.TrendStats;
import com.pcbtest.dashboard.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/stats")
@RequiredArgsConstructor
public class StatsController {

    private final StatsService statsService;

    @GetMapping("/summary")
    public ResponseEntity<SummaryStats> getSummary() {
        return ResponseEntity.ok(statsService.getSummary());
    }

    @GetMapping("/trend")
    public ResponseEntity<TrendStats> getTrend(@RequestParam(defaultValue = "14") int days) {
        return ResponseEntity.ok(statsService.getTrend(days));
    }
}
