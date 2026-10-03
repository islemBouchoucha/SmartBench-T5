package com.pcbtest.dashboard.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

@Entity
@Table(name = "visual_results")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VisualResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne
    @JoinColumn(name = "pcb_test_id", unique = true)
    private PcbTest pcbTest;

    @Column(name = "image_path")
    private String imagePath;

    @Column(name = "missing_components_count")
    @Builder.Default
    private Integer missingComponentsCount = 0;

    @Column(name = "misplaced_components_count")
    @Builder.Default
    private Integer misplacedComponentsCount = 0;

    @Column(name = "solder_defects_count")
    @Builder.Default
    private Integer solderDefectsCount = 0;

    @Column(name = "damaged_connectors_count")
    @Builder.Default
    private Integer damagedConnectorsCount = 0;

    @Column(name = "is_blocking_anomaly")
    @Builder.Default
    private Boolean isBlockingAnomaly = false;

    @Column(name = "ai_confidence_score", precision = 5, scale = 2)
    private BigDecimal aiConfidenceScore;

    @Column(name = "visual_status", nullable = false, length = 20)
    private String visualStatus; // PASS, FAIL
}
