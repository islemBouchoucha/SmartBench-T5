import type { Plugin } from 'chart.js';

/**
 * Lightens or darkens a hex color by a percentage.
 * shadeColor('#0d6efd', -20) => darker shade
 * shadeColor('#0d6efd', 20)  => lighter shade
 */
function shadeColor(color: string, percent: number): string {
  if (!color || !color.startsWith('#')) return color;
  let hex = color.slice(1);
  if (hex.length === 3) {
    hex = hex.split('').map((c) => c + c).join('');
  }
  const num = parseInt(hex, 16);
  let r = (num >> 16) + Math.round(2.55 * percent);
  let g = ((num >> 8) & 0x00ff) + Math.round(2.55 * percent);
  let b = (num & 0x0000ff) + Math.round(2.55 * percent);
  r = Math.min(255, Math.max(0, r));
  g = Math.min(255, Math.max(0, g));
  b = Math.min(255, Math.max(0, b));
  return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1)}`;
}

/**
 * Draws each bar as an isometric-looking 3D block by adding a top face
 * and a right-side face, extruded from the flat bar Chart.js already drew.
 */
export const bar3dPlugin: Plugin<'bar'> = {
  id: 'bar3d',
  afterDatasetsDraw(chart) {
    const depth = (chart.options.plugins as any)?.bar3d?.depth ?? 10;
    const ctx = chart.ctx;

    chart.data.datasets.forEach((_dataset, datasetIndex) => {
      const meta = chart.getDatasetMeta(datasetIndex);
      if (meta.type !== 'bar' || meta.hidden) return;

      meta.data.forEach((bar: any) => {
        const props = bar.getProps(['x', 'y', 'width', 'base'], true);
        const { x, y, width, base } = props;
        if (y === undefined || Number.isNaN(y)) return;

        const left = x - width / 2;
        const right = x + width / 2;
        const top = y;
        const bottom = base;
        const baseColor: string = (bar.options?.backgroundColor as string) || '#0d6efd';
        const topColor = shadeColor(baseColor, 22);
        const sideColor = shadeColor(baseColor, -22);

        ctx.save();

        // Top face (parallelogram)
        ctx.beginPath();
        ctx.moveTo(left, top);
        ctx.lineTo(left + depth * 0.6, top - depth);
        ctx.lineTo(right + depth * 0.6, top - depth);
        ctx.lineTo(right, top);
        ctx.closePath();
        ctx.fillStyle = topColor;
        ctx.fill();

        // Right side face (parallelogram)
        ctx.beginPath();
        ctx.moveTo(right, top);
        ctx.lineTo(right + depth * 0.6, top - depth);
        ctx.lineTo(right + depth * 0.6, bottom - depth);
        ctx.lineTo(right, bottom);
        ctx.closePath();
        ctx.fillStyle = sideColor;
        ctx.fill();

        ctx.restore();
      });
    });
  }
};

/**
 * Draws an extruded "cylinder" underneath a doughnut/pie chart's arcs so it
 * reads as a solid 3D puck rather than a flat ring.
 */
export const doughnut3dPlugin: Plugin<'doughnut' | 'pie'> = {
  id: 'doughnut3d',
  beforeDatasetsDraw(chart) {
    const depth = (chart.options.plugins as any)?.doughnut3d?.depth ?? 16;
    const ctx = chart.ctx;

    chart.data.datasets.forEach((_dataset, datasetIndex) => {
      const meta = chart.getDatasetMeta(datasetIndex);
      if ((meta.type !== 'doughnut' && meta.type !== 'pie') || meta.hidden) return;

      meta.data.forEach((arc: any) => {
        const props = arc.getProps(
          ['x', 'y', 'startAngle', 'endAngle', 'innerRadius', 'outerRadius'],
          true
        );
        const { x, y, startAngle, endAngle, innerRadius, outerRadius } = props;
        if (outerRadius === undefined || Number.isNaN(outerRadius)) return;

        const baseColor: string = (arc.options?.backgroundColor as string) || '#0d6efd';
        const sideColor = shadeColor(baseColor, -28);

        ctx.save();
        ctx.fillStyle = sideColor;
        for (let d = depth; d > 0; d -= 1) {
          ctx.beginPath();
          ctx.arc(x, y + d, outerRadius, startAngle, endAngle, false);
          ctx.arc(x, y + d, innerRadius, endAngle, startAngle, true);
          ctx.closePath();
          ctx.fill();
        }
        ctx.restore();
      });
    });
  }
};

/** Simple 3D pointer-tilt effect: call on mousemove/mouseleave of a card element. */
export function apply3dTilt(el: HTMLElement, event: MouseEvent, maxTilt = 6): void {
  const rect = el.getBoundingClientRect();
  const px = (event.clientX - rect.left) / rect.width;
  const py = (event.clientY - rect.top) / rect.height;
  const rotateY = (px - 0.5) * maxTilt * 2;
  const rotateX = (0.5 - py) * maxTilt * 2;
  el.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(0)`;
}

export function reset3dTilt(el: HTMLElement): void {
  el.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0)';
}
