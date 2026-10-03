import {
  AfterViewInit,
  ChangeDetectorRef,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  PLATFORM_ID,
  ViewChild,
  inject
} from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Chart, registerables } from 'chart.js';
import { Stats } from '../../services/stats';
import { PcbTest } from '../../services/pcb-test';
import { ElectricalStat, SummaryStats, TrendStats } from '../../models/stats';
import { PcbTestSummary } from '../../models/pcb-test';
import { Sidebar } from '../sidebar/sidebar';
import { TranslatePipe } from '../../pipes/translate';
import { apply3dTilt, bar3dPlugin, doughnut3dPlugin, reset3dTilt } from './chart3d-plugins';

type ElectricalKey = 'voltage' | 'current' | 'resistance' | 'power' | 'temperature';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, Sidebar, TranslatePipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit, AfterViewInit, OnDestroy {
  private platformId = inject(PLATFORM_ID);
  private cdr = inject(ChangeDetectorRef);

  @ViewChild('defectCanvas') defectCanvasRef?: ElementRef<HTMLCanvasElement>;
  @ViewChild('statusCanvas') statusCanvasRef?: ElementRef<HTMLCanvasElement>;
  @ViewChild('trendCanvas') trendCanvasRef?: ElementRef<HTMLCanvasElement>;

  private defectChart?: Chart;
  private statusChart?: Chart;
  private trendChart?: Chart;
  private viewReady = false;

  summary: SummaryStats | null = null;
  trend: TrendStats | null = null;
  tests: PcbTestSummary[] = [];

  isLoading = true;
  errorMessage = '';

  statusFilter = '';
  searchFilter = '';
  currentPage = 0;
  totalPages = 0;
  pageSize = 10;

  // Plages d'affichage des jauges électriques (à ajuster selon vos specs PCB).
  // Ces bornes ne servent qu'à positionner l'aiguille de la jauge (0-100%),
  // elles ne représentent pas un seuil de pass/fail.
  private readonly electricalRanges: Record<ElectricalKey, { min: number; max: number; unit: string; label: string; icon: string }> = {
    voltage: { min: 0, max: 24, unit: 'V', label: 'Tension', icon: 'fa-bolt' },
    current: { min: 0, max: 10, unit: 'A', label: 'Courant', icon: 'fa-wave-square' },
    resistance: { min: 0, max: 1000, unit: 'Ω', label: 'Résistance', icon: 'fa-microchip' },
    power: { min: 0, max: 250, unit: 'W', label: 'Puissance', icon: 'fa-plug' },
    temperature: { min: 0, max: 100, unit: '°C', label: 'Température', icon: 'fa-temperature-half' }
  };

  constructor(
    private statsService: Stats,
    private pcbTestService: PcbTest
  ) {
    if (isPlatformBrowser(this.platformId)) {
      Chart.register(...registerables, bar3dPlugin, doughnut3dPlugin);
    }
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.loadDashboard();
    } else {
      this.isLoading = false;
    }
  }

  ngAfterViewInit(): void {
    this.viewReady = true;
    this.renderCharts();
  }

  ngOnDestroy(): void {
    this.defectChart?.destroy();
    this.statusChart?.destroy();
    this.trendChart?.destroy();
  }

  loadDashboard(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.statsService.getSummary().subscribe({
      next: (data) => {
        this.summary = data;
        this.cdr.markForCheck();
        this.renderCharts();
      },
      error: (err) => {
        this.handleError(err, 'Impossible de charger les statistiques.');
        this.cdr.markForCheck();
      }
    });

    this.statsService.getTrend(14).subscribe({
      next: (data) => {
        this.trend = data;
        this.cdr.markForCheck();
        this.renderCharts();
      },
      error: (err) => {
        this.handleError(err, 'Impossible de charger la tendance.');
        this.cdr.markForCheck();
      }
    });

    this.loadTests();
  }

  loadTests(): void {
    this.isLoading = true;
    this.pcbTestService
      .listTests(this.currentPage, this.pageSize, this.statusFilter || undefined, this.searchFilter || undefined)
      .subscribe({
        next: (data) => {
          this.tests = data.content;
          this.totalPages = data.totalPages;
          this.isLoading = false;
          this.cdr.markForCheck();
        },
        error: (err) => {
          this.handleError(err, 'Impossible de charger la liste des tests.');
          this.isLoading = false;
          this.cdr.markForCheck();
        }
      });
  }

  private handleError(err: any, fallbackMessage: string): void {
    if (err?.status === 401 || err?.status === 403) {
      this.errorMessage = 'Session expirée ou non autorisée. Veuillez vous reconnecter.';
    } else {
      this.errorMessage = fallbackMessage;
    }
  }

  onFilterChange(): void {
    this.currentPage = 0;
    this.loadTests();
  }

  goToPage(page: number): void {
    if (page >= 0 && page < this.totalPages) {
      this.currentPage = page;
      this.loadTests();
    }
  }

  get defectEntries(): { name: string; count: number }[] {
    if (!this.summary) return [];
    return Object.entries(this.summary.defectBreakdown).map(([name, count]) => ({ name, count }));
  }

  statusClass(status: string): string {
    switch (status?.toUpperCase()) {
      case 'PASS': return 'badge badge-pass';
      case 'FAIL': return 'badge badge-fail';
      case 'BLOCKED': return 'badge badge-blocked';
      default: return 'badge';
    }
  }

  /**
   * Paramètres électriques à afficher : utilise les agrégats du backend
   * (summary.xStats) s'ils existent, sinon calcule une moyenne/min/max
   * approximative à partir des tests actuellement chargés (page courante).
   * Un paramètre n'apparaît que si au moins une valeur est disponible.
   */
  get electricalParams(): {
    key: string; label: string; unit: string; icon: string;
    avg: number; min: number; max: number; percent: number;
  }[] {
    const mapping: { key: ElectricalKey; statKey: keyof SummaryStats; field: keyof PcbTestSummary }[] = [
      { key: 'voltage', statKey: 'voltageStats', field: 'voltage' },
      { key: 'current', statKey: 'currentStats', field: 'current' },
      { key: 'resistance', statKey: 'resistanceStats', field: 'resistance' },
      { key: 'power', statKey: 'powerStats', field: 'power' },
      { key: 'temperature', statKey: 'temperatureStats', field: 'temperature' }
    ];

    const results: { key: string; label: string; unit: string; icon: string; avg: number; min: number; max: number; percent: number }[] = [];

    for (const { key, statKey, field } of mapping) {
      const range = this.electricalRanges[key];
      let stat: ElectricalStat | undefined = this.summary?.[statKey] as ElectricalStat | undefined;

      if (!stat) {
        const values = this.tests
          .map((t) => t[field] as unknown as number | undefined)
          .filter((v): v is number => v !== undefined && v !== null && !Number.isNaN(v));
        if (values.length === 0) continue;
        stat = {
          avg: values.reduce((a, b) => a + b, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values)
        };
      }

      const percent = Math.min(100, Math.max(0, ((stat.avg - range.min) / (range.max - range.min)) * 100));
      results.push({ key, label: range.label, unit: range.unit, icon: range.icon, avg: stat.avg, min: stat.min, max: stat.max, percent });
    }

    return results;
  }

  get hasElectricalData(): boolean {
    return this.electricalParams.length > 0;
  }

  gaugeStyle(percent: number): { [k: string]: string } {
    return {
      background: `conic-gradient(#0d6efd ${percent}%, #e9ecf3 ${percent}% 100%)`
    };
  }

  onCardTilt(event: MouseEvent): void {
    apply3dTilt(event.currentTarget as HTMLElement, event, 5);
  }

  onCardTiltReset(event: MouseEvent): void {
    reset3dTilt(event.currentTarget as HTMLElement);
  }

  // ---- Chart rendering -----------------------------------------------

  private renderCharts(): void {
    if (!this.viewReady || !isPlatformBrowser(this.platformId)) return;
    this.renderDefectChart();
    this.renderStatusChart();
    this.renderTrendChart();
  }

  private renderDefectChart(): void {
    const canvas = this.defectCanvasRef?.nativeElement;
    if (!canvas || !this.summary) return;

    const entries = this.defectEntries;
    const palette = ['#0d6efd', '#6f42c1', '#d63384', '#fd7e14', '#20c997', '#0dcaf0', '#dc3545'];
    const labels = entries.map((e) => e.name);
    const data = entries.map((e) => e.count);
    const colors = labels.map((_, i) => palette[i % palette.length]);

    this.defectChart?.destroy();
    this.defectChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Défauts',
            data,
            backgroundColor: colors,
            borderWidth: 0,
            borderRadius: 0,
            maxBarThickness: 34
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: { padding: { top: 16, right: 16 } },
        animation: { duration: 700, easing: 'easeOutQuart' },
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: '#00224dee', padding: 10, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#7b8291', font: { size: 11 } } },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { color: '#7b8291', precision: 0 }
          }
        }
      }
    });
  }

  private renderStatusChart(): void {
    const canvas = this.statusCanvasRef?.nativeElement;
    if (!canvas || !this.summary) return;

    const data = [this.summary.passCount, this.summary.failCount, this.summary.blockedCount];
    const colors = ['#16a34a', '#dc2626', '#d97706'];

    this.statusChart?.destroy();
    this.statusChart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Pass', 'Fail', 'Bloqué'],
        datasets: [
          {
            data,
            backgroundColor: colors,
            borderWidth: 3,
            borderColor: '#ffffff',
            hoverOffset: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        layout: { padding: { bottom: 18 } },
        animation: { duration: 800, easing: 'easeOutQuart' },
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#7b8291', boxWidth: 10, boxHeight: 10, padding: 14, font: { size: 11.5 } }
          },
          tooltip: { backgroundColor: '#00224dee', padding: 10, cornerRadius: 8 },
          ...( { doughnut3d: { depth: 16 } } as any)
        }
      }
    });
  }

  private renderTrendChart(): void {
    const canvas = this.trendCanvasRef?.nativeElement;
    if (!canvas || !this.trend) return;

    const labels = this.trend.points.map((p) => p.date.slice(5));
    const ctx = canvas.getContext('2d')!;

    const passGrad = ctx.createLinearGradient(0, 0, 0, 220);
    passGrad.addColorStop(0, 'rgba(22, 163, 74, 0.45)');
    passGrad.addColorStop(1, 'rgba(22, 163, 74, 0.02)');

    const failGrad = ctx.createLinearGradient(0, 0, 0, 220);
    failGrad.addColorStop(0, 'rgba(220, 38, 38, 0.35)');
    failGrad.addColorStop(1, 'rgba(220, 38, 38, 0.02)');

    const blockedGrad = ctx.createLinearGradient(0, 0, 0, 220);
    blockedGrad.addColorStop(0, 'rgba(217, 119, 6, 0.3)');
    blockedGrad.addColorStop(1, 'rgba(217, 119, 6, 0.02)');

    this.trendChart?.destroy();
    this.trendChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Pass',
            data: this.trend.points.map((p) => p.pass),
            borderColor: '#16a34a',
            backgroundColor: passGrad,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2.5
          },
          {
            label: 'Fail',
            data: this.trend.points.map((p) => p.fail),
            borderColor: '#dc2626',
            backgroundColor: failGrad,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2.5
          },
          {
            label: 'Bloqué',
            data: this.trend.points.map((p) => p.blocked),
            borderColor: '#d97706',
            backgroundColor: blockedGrad,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 5,
            borderWidth: 2.5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        animation: { duration: 700, easing: 'easeOutQuart' },
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: '#00224dee', padding: 10, cornerRadius: 8 }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#7b8291', font: { size: 10.5 }, maxRotation: 0 } },
          y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { color: '#7b8291', precision: 0 } }
        }
      }
    });
  }
}
