package com.pcbtest.dashboard.controller;

import com.pcbtest.dashboard.dto.PcbTestDtos.*;
import com.pcbtest.dashboard.service.PcbTestService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/tests")
@RequiredArgsConstructor
public class PcbTestController {

    private final PcbTestService pcbTestService;

    @GetMapping
    public ResponseEntity<Page<PcbTestSummary>> listTests(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String operator,
            @PageableDefault(size = 20, sort = "testDate") Pageable pageable) {
        return ResponseEntity.ok(pcbTestService.listTests(status, search, operator, pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<PcbTestDetail> getTest(@PathVariable Long id) {
        return ResponseEntity.ok(pcbTestService.getTestDetail(id));
    }

    // Utilisé par l'API du banc de test / du service qui orchestre YOLO + Isolation Forest
    // pour enregistrer le résultat complet d'un cycle de test.
    @PostMapping
    public ResponseEntity<PcbTestDetail> createTest(@Valid @RequestBody CreatePcbTestRequest request) {
        return ResponseEntity.ok(pcbTestService.createTest(request));
    }
}
