import { createChart } from "lightweight-charts";

const createResponsiveChart = (container: HTMLElement, options: any) => {
  const chart = createChart(container, options);
  new ResizeObserver(() => {
    chart.applyOptions({ width: container.clientWidth });
    chart.timeScale().fitContent();
  }).observe(container);
  return chart;
};

export { createResponsiveChart };
