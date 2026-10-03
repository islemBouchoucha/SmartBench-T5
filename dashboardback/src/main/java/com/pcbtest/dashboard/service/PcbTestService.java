package com.pcbtest.dashboard.service;

import com.pcbtest.dashboard.dto.PcbTestDtos.*;
import com.pcbtest.dashboard.entity.ElectricalResult;
import com.pcbtest.dashboard.entity.PcbTest;
import com.pcbtest.dashboard.entity.User;
import com.pcbtest.dashboard.entity.VisualResult;
import com.pcbtest.dashboard.exception.ResourceNotFoundException;
import com.pcbtest.dashboard.repository.PcbTestRepository;
import com.pcbtest.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
@RequiredArgsConstructor
public class PcbTestService {

    private final PcbTestRepository pcbTestRepository;
    private final UserRepository userRepository;

    public Page<PcbTestSummary> listTests(String status, String search, String operator, Pageable pageable) {
        Page<PcbTest> page;
        if (StringUtils.hasText(operator)) {
            page = pcbTestRepository.findByOperator_UsernameIgnoreCase(operator, pageable);
        } else if (StringUtils.hasText(status)) {
            page = pcbTestRepository.findByOverallStatus(status.toUpperCase(), pageable);
        } else if (StringUtils.hasText(search)) {
            page = pcbTestRepository.findBySerialNumberContainingIgnoreCase(search, pageable);
        } else {
            page = pcbTestRepository.findAll(pageable);
        }
        return page.map(this::toSummary);
    }

    public PcbTestDetail getTestDetail(Long id) {
        PcbTest test = pcbTestRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Test introuvable, id=" + id));
        return toDetail(test);
    }

    @Transactional
    public PcbTestDetail createTest(CreatePcbTestRequest request) {
        PcbTest test = new PcbTest();
        test.setSerialNumber(request.serialNumber());

        if (request.operatorId() != null) {
            User operator = userRepository.findById(request.operatorId())
                    .orElseThrow(() -> new ResourceNotFoundException("Opérateur introuvable, id=" + request.operatorId()));
            test.setOperator(operator);
        }

        VisualResultDto v = request.visualResult();
        ElectricalResultDto e = request.electricalResult();

        boolean visualFail = v != null && "FAIL".equalsIgnoreCase(v.visualStatus());
        boolean electricalFail = e != null &&
                ("FAIL".equalsIgnoreCase(e.classicStatus()) || "ANOMALY".equalsIgnoreCase(e.aiStatus()));
        boolean blocking = v != null && Boolean.TRUE.equals(v.isBlockingAnomaly());

        test.setOverallStatus(blocking ? "BLOCKED" : (visualFail || electricalFail ? "FAIL" : "PASS"));

        PcbTest savedTest = pcbTestRepository.save(test);

        if (v != null) {
            VisualResult visualResult = VisualResult.builder()
                    .pcbTest(savedTest)
                    .imagePath(v.imagePath())
                    .missingComponentsCount(v.missingComponentsCount())
                    .misplacedComponentsCount(v.misplacedComponentsCount())
                    .solderDefectsCount(v.solderDefectsCount())
                    .damagedConnectorsCount(v.damagedConnectorsCount())
                    .isBlockingAnomaly(v.isBlockingAnomaly())
                    .aiConfidenceScore(v.aiConfidenceScore())
                    .visualStatus(v.visualStatus())
                    .build();
            savedTest.setVisualResult(visualResult);
        }

        if (e != null) {
            ElectricalResult electricalResult = ElectricalResult.builder()
                    .pcbTest(savedTest)
                    .tension(e.tension())
                    .courant(e.courant())
                    .gainMes1(e.gainMes1())
                    .gainMes2(e.gainMes2())
                    .gainMes3(e.gainMes3())
                    .puissance(e.puissance())
                    .rms(e.rms())
                    .temperature(e.temperature())
                    .classicStatus(e.classicStatus())
                    .aiAnomalyScore(e.aiAnomalyScore())
                    .aiStatus(e.aiStatus())
                    .build();
            savedTest.setElectricalResult(electricalResult);
        }

        PcbTest finalTest = pcbTestRepository.save(savedTest);
        return toDetail(finalTest);
    }

    private PcbTestSummary toSummary(PcbTest t) {
        return new PcbTestSummary(
                t.getId(),
                t.getSerialNumber(),
                t.getTestDate(),
                t.getOverallStatus(),
                t.getOperator() != null ? t.getOperator().getUsername() : null,
                t.getVisualResult() != null ? t.getVisualResult().getVisualStatus() : null,
                t.getElectricalResult() != null ? t.getElectricalResult().getClassicStatus() : null
        );
    }

    private PcbTestDetail toDetail(PcbTest t) {
        VisualResultDto visualDto = null;
        if (t.getVisualResult() != null) {
            VisualResult v = t.getVisualResult();
            visualDto = new VisualResultDto(
                    v.getImagePath(), v.getMissingComponentsCount(), v.getMisplacedComponentsCount(),
                    v.getSolderDefectsCount(), v.getDamagedConnectorsCount(), v.getIsBlockingAnomaly(),
                    v.getAiConfidenceScore(), v.getVisualStatus()
            );
        }

        ElectricalResultDto electricalDto = null;
        if (t.getElectricalResult() != null) {
            ElectricalResult e = t.getElectricalResult();
            electricalDto = new ElectricalResultDto(
                    e.getTension(), e.getCourant(), e.getGainMes1(),
                    e.getGainMes2(), e.getGainMes3(), e.getPuissance(),
                    e.getRms(), e.getTemperature(), e.getClassicStatus(),
                    e.getAiAnomalyScore(), e.getAiStatus()
            );
        }

        return new PcbTestDetail(
                t.getId(), t.getSerialNumber(), t.getTestDate(), t.getOverallStatus(),
                t.getOperator() != null ? t.getOperator().getUsername() : null,
                visualDto, electricalDto
        );
    }
}
