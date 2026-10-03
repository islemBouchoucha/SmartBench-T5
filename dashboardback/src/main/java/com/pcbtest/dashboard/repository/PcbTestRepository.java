package com.pcbtest.dashboard.repository;

import com.pcbtest.dashboard.entity.PcbTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface PcbTestRepository extends JpaRepository<PcbTest, Long> {

    Page<PcbTest> findByOverallStatus(String status, Pageable pageable);

    Page<PcbTest> findBySerialNumberContainingIgnoreCase(String serialNumber, Pageable pageable);

    Page<PcbTest> findByOperator_UsernameIgnoreCase(String username, Pageable pageable);

    long countByOverallStatus(String status);

    @Query("SELECT t FROM PcbTest t WHERE t.testDate >= :from ORDER BY t.testDate DESC")
    List<PcbTest> findRecentTests(@Param("from") LocalDateTime from);

    @Query("SELECT FUNCTION('DATE', t.testDate) as day, t.overallStatus as status, COUNT(t) as total " +
           "FROM PcbTest t WHERE t.testDate >= :from " +
           "GROUP BY FUNCTION('DATE', t.testDate), t.overallStatus " +
           "ORDER BY day ASC")
    List<Object[]> countTestsByDayAndStatus(@Param("from") LocalDateTime from);
}
