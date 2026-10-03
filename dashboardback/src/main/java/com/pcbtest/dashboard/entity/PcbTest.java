package com.pcbtest.dashboard.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "pcb_tests")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PcbTest {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "serial_number", nullable = false, length = 100)
    private String serialNumber;

    @Column(name = "test_date")
    private LocalDateTime testDate;

    @Column(name = "overall_status", nullable = false, length = 20)
    private String overallStatus; // PASS, FAIL, BLOCKED

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "operator_id")
    private User operator;

    @OneToOne(mappedBy = "pcbTest", cascade = CascadeType.ALL, orphanRemoval = true)
    private VisualResult visualResult;

    @OneToOne(mappedBy = "pcbTest", cascade = CascadeType.ALL, orphanRemoval = true)
    private ElectricalResult electricalResult;

    @PrePersist
    protected void onCreate() {
        if (this.testDate == null) {
            this.testDate = LocalDateTime.now();
        }
    }
}
