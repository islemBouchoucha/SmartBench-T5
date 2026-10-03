package com.pcbtest.dashboard.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

@Entity
@Table(name = "electrical_results")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ElectricalResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "pcb_test_id", unique = true)
    private PcbTest pcbTest;

    @Column(name = "tension", precision = 10, scale = 3)
    private BigDecimal tension;

    @Column(name = "courant", precision = 10, scale = 3)
    private BigDecimal courant;

    @Column(name = "gain_mes1", precision = 10, scale = 3)
    private BigDecimal gainMes1;

    @Column(name = "gain_mes2", precision = 10, scale = 3)
    private BigDecimal gainMes2;

    @Column(name = "gain_mes3", precision = 10, scale = 3)
    private BigDecimal gainMes3;

    @Column(name = "puissance", precision = 10, scale = 3)
    private BigDecimal puissance;

    @Column(name = "rms", precision = 10, scale = 3)
    private BigDecimal rms;

    @Column(name = "temperature", precision = 10, scale = 3)
    private BigDecimal temperature;

    @Column(name = "classic_status", nullable = false, length = 20)
    private String classicStatus; // PASS, FAIL

    @Column(name = "ai_anomaly_score", precision = 10, scale = 4)
    private BigDecimal aiAnomalyScore;

    @Column(name = "ai_status", nullable = false, length = 20)
    private String aiStatus; // NORMAL, ANOMALY
}
