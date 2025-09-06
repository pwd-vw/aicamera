<template>
  <div class="analytics-view">
    <header class="view-header">
      <h1>Analytics</h1>
      <div class="filters">
        <label>
          Range:
          <select v-model="timeBucket" class="select">
            <option value="hour">Last 24h</option>
            <option value="day">Last 14d</option>
          </select>
        </label>
        <input type="date" v-model="startDate" class="select" />
        <input type="date" v-model="endDate" class="select" />
        <button class="btn-secondary" @click="refreshAll" :disabled="loading">{{ loading ? 'Loading…' : 'Refresh' }}</button>
      </div>
    </header>

    <section class="grid-3">
      <div class="card metric">
        <div class="metric-label">Cameras</div>
        <div class="metric-value">{{ edgeSummary?.totalCameras || 0 }}</div>
        <div class="metric-sub">
          <span class="ok">Active {{ edgeSummary?.activeCameras || 0 }}</span>
          <span>Inactive {{ edgeSummary?.inactiveCameras || 0 }}</span>
          <span class="err">Error {{ edgeSummary?.errorCameras || 0 }}</span>
        </div>
      </div>
      <div class="card metric">
        <div class="metric-label">Avg API Latency</div>
        <div class="metric-value">{{ network?.api.latencyMsAvg || 0 }} ms</div>
        <div class="metric-sub">p95 {{ network?.api.latencyMsP95 || 0 }} ms</div>
      </div>
      <div class="card metric">
        <div class="metric-label">Detections ({{ timeBucket }})</div>
        <div class="metric-value">{{ totalDetections }}</div>
        <div class="sparkline">
          <svg :viewBox="`0 0 ${sparkW} ${sparkH}`" preserveAspectRatio="none">
            <polyline :points="sparkPoints" fill="none" stroke="#2563eb" stroke-width="2" />
          </svg>
        </div>
      </div>
    </section>

    <section class="grid-2">
      <div class="card">
        <h3>Edge Status</h3>
        <div class="edge-grid">
          <div class="edge-summary">
            <div class="bar">
              <div class="bar-ok" :style="{ width: pct(edgeSummary?.activeCameras, edgeSummary?.totalCameras) }"></div>
              <div class="bar-warn" :style="{ width: pct(edgeSummary?.inactiveCameras, edgeSummary?.totalCameras) }"></div>
              <div class="bar-err" :style="{ width: pct(edgeSummary?.errorCameras, edgeSummary?.totalCameras) }"></div>
            </div>
            <div class="utilization">
              <div>CPU Avg: {{ edgeSummary?.cpuUtilizationAvg }}%</div>
              <div>Mem Avg: {{ edgeSummary?.memoryUtilizationAvg }}%</div>
            </div>
          </div>
          <table class="mini-table">
            <thead>
              <tr>
                <th>Camera</th>
                <th>Status</th>
                <th>CPU%</th>
                <th>Mem%</th>
                <th>Drop fps</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cam in topCameras" :key="cam.cameraId">
                <td>{{ cam.name }}</td>
                <td><span :class="['badge', cam.status]">{{ cam.status }}</span></td>
                <td>{{ cam.cpuUtilization }}</td>
                <td>{{ cam.memoryUtilization }}</td>
                <td>{{ cam.droppedFramesRate }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <h3>Unified Network</h3>
        <div class="network-grid">
          <div class="net-item">
            <div class="net-title">API</div>
            <div class="net-status" :class="network?.api.status">{{ network?.api.status }}</div>
            <div class="net-metrics">{{ network?.api.latencyMsAvg }}ms avg • {{ network?.api.latencyMsP95 }}ms p95</div>
            <div class="net-metrics">{{ network?.api.requestRatePerMin }}/min</div>
          </div>
          <div class="net-item">
            <div class="net-title">WebSocket</div>
            <div class="net-status" :class="network?.websocket.status">{{ network?.websocket.status }}</div>
            <div class="net-metrics">{{ network?.websocket.latencyMsAvg }}ms avg</div>
            <div class="net-metrics">{{ network?.websocket.msgRatePerMin }}/min</div>
          </div>
          <div class="net-item">
            <div class="net-title">MQTT</div>
            <div class="net-status" :class="network?.mqtt.status">{{ network?.mqtt.status }}</div>
            <div class="net-metrics">{{ network?.mqtt.latencyMsAvg }}ms avg</div>
            <div class="net-metrics">{{ network?.mqtt.msgRatePerMin }}/min</div>
          </div>
        </div>
      </div>
    </section>

    <section class="grid-2">
      <div class="card">
        <h3>Detections Over Time</h3>
        <div class="chart">
          <svg :viewBox="`0 0 ${chartW} ${chartH}`" preserveAspectRatio="none">
            <polyline :points="linePoints" fill="none" stroke="#2563eb" stroke-width="2" />
            <g v-for="(p, idx) in series" :key="idx">
              <circle :cx="xScale(idx)" :cy="yScale(p.count)" r="2" fill="#1d4ed8" />
            </g>
          </svg>
        </div>
      </div>

      <div class="card">
        <h3>Top License Plates</h3>
        <table class="mini-table">
          <thead>
            <tr>
              <th>Plate</th>
              <th>Count</th>
              <th>First Seen</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in topPlates" :key="p.licensePlate">
              <td>{{ p.licensePlate }}</td>
              <td>{{ p.count }}</td>
              <td>{{ formatDate(p.firstSeen) }}</td>
              <td>{{ formatDate(p.lastSeen) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h3>Detections by Location</h3>
      <div class="location-grid">
        <div class="legend">
          <span class="dot low"></span> Low
          <span class="dot med"></span> Medium
          <span class="dot high"></span> High
        </div>
        <div class="locations">
          <div v-for="(b, i) in locations.buckets" :key="i" class="loc-item">
            <div class="loc-coord">{{ b.lat.toFixed(4) }}, {{ b.lng.toFixed(4) }}</div>
            <div class="loc-bar">
              <div class="loc-fill" :class="densityClass(b.count)" :style="{ width: barWidth(b.count) }"></div>
            </div>
            <div class="loc-count">{{ b.count }}</div>
          </div>
        </div>
        <router-link to="/map" class="btn-secondary">Open Map</router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { analyticsService, type EdgeStatusSummary, type NetworkStats, type DetectionTimeSeriesPoint, type DetectionsByLocation, type TopPlateItem } from '../services/analytics.service';

const loading = ref(false);
const edgeSummary = ref<EdgeStatusSummary | null>(null);
const network = ref<NetworkStats | null>(null);
const series = ref<DetectionTimeSeriesPoint[]>([]);
const locations = ref<DetectionsByLocation>({ buckets: [] });
const topPlates = ref<TopPlateItem[]>([]);

const timeBucket = ref<'hour' | 'day'>('hour');
const startDate = ref<string>('');
const endDate = ref<string>('');

const chartW = 600;
const chartH = 220;
const sparkW = 200;
const sparkH = 40;

const totalDetections = computed(() => series.value.reduce((s, p) => s + p.count, 0));

const xScale = (idx: number) => (idx / Math.max(1, series.value.length - 1)) * chartW;
const yScale = (count: number) => {
  const max = Math.max(1, ...series.value.map(p => p.count));
  const y = chartH - (count / max) * (chartH - 20) - 10;
  return y;
};

const linePoints = computed(() => series.value.map((p, i) => `${xScale(i)},${yScale(p.count)}`).join(' '));
const sparkPoints = computed(() => {
  const max = Math.max(1, ...series.value.map(p => p.count));
  return series.value.map((p, i) => {
    const x = (i / Math.max(1, series.value.length - 1)) * sparkW;
    const y = sparkH - (p.count / max) * (sparkH - 6) - 3;
    return `${x},${y}`;
  }).join(' ');
});

const topCameras = computed(() => edgeSummary.value?.perCamera?.slice(0, 6) || []);

function pct(a?: number, b?: number) {
  if (!a || !b) return '0%';
  return `${Math.round((a / b) * 100)}%`;
}

function barWidth(count: number) {
  const max = Math.max(1, ...locations.value.buckets.map(b => b.count));
  return `${Math.round((count / max) * 100)}%`;
}

function densityClass(count: number) {
  if (count >= 60) return 'high';
  if (count >= 30) return 'med';
  return 'low';
}

function formatDate(d: string) {
  return new Date(d).toLocaleString();
}

async function refreshAll() {
  loading.value = true;
  try {
    const params: any = { bucket: timeBucket.value };
    if (startDate.value) params.startDate = new Date(startDate.value).toISOString();
    if (endDate.value) params.endDate = new Date(endDate.value).toISOString();

    const [edge, net, ts, loc, plates] = await Promise.all([
      analyticsService.getEdgeStatusSummary(),
      analyticsService.getNetworkStats(),
      analyticsService.getDetectionTimeSeries(params),
      analyticsService.getDetectionsByLocation(params),
      analyticsService.getTopPlates(params),
    ]);
    edgeSummary.value = edge;
    network.value = net;
    series.value = ts;
    locations.value = loc;
    topPlates.value = plates;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  // Default range: last 24 hours for hour bucket
  const end = new Date();
  const start = new Date(end);
  start.setHours(end.getHours() - 24);
  startDate.value = start.toISOString().slice(0, 10);
  endDate.value = end.toISOString().slice(0, 10);
  refreshAll();
});
</script>

<style scoped>
.analytics-view {
  padding: 1rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.filters {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}
.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.metric-label { color: #6b7280; font-size: 0.875rem; }
.metric-value { font-size: 1.75rem; font-weight: 600; color: #111827; }
.metric-sub { color: #6b7280; font-size: 0.875rem; display: flex; gap: 0.5rem; }
.metric-sub .ok { color: #10b981; }
.metric-sub .err { color: #ef4444; }
.sparkline { height: 40px; }

.edge-grid { display: grid; grid-template-columns: 1fr; gap: 0.75rem; }
.edge-summary .bar { display: flex; height: 10px; background: #f3f4f6; border-radius: 999px; overflow: hidden; }
.bar-ok { background: #10b981; }
.bar-warn { background: #f59e0b; }
.bar-err { background: #ef4444; }
.utilization { margin-top: 0.5rem; display: flex; gap: 1rem; color: #374151; font-size: 0.9rem; }

.mini-table { width: 100%; border-collapse: collapse; }
.mini-table th, .mini-table td { text-align: left; padding: 0.5rem; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem; }
.badge { padding: 0.125rem 0.5rem; border-radius: 999px; font-size: 0.75rem; text-transform: capitalize; }
.badge.active { background: #ecfdf5; color: #065f46; }
.badge.inactive { background: #f3f4f6; color: #374151; }
.badge.error { background: #fef2f2; color: #991b1b; }

.network-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; }
.net-item { border: 1px solid #f3f4f6; border-radius: 0.5rem; padding: 0.75rem; }
.net-title { font-weight: 600; color: #111827; }
.net-status { text-transform: uppercase; font-size: 0.75rem; margin: 0.25rem 0; }
.net-status.up { color: #10b981; }
.net-status.down { color: #ef4444; }
.net-metrics { color: #374151; font-size: 0.875rem; }

.chart { width: 100%; height: 240px; }

.location-grid { display: grid; gap: 0.75rem; }
.legend { display: flex; gap: 0.5rem; align-items: center; color: #6b7280; }
.dot { width: 10px; height: 10px; border-radius: 999px; display: inline-block; }
.dot.low { background: #bfdbfe; }
.dot.med { background: #60a5fa; }
.dot.high { background: #2563eb; }
.locations { display: grid; gap: 0.25rem; }
.loc-item { display: grid; grid-template-columns: 1fr 5fr auto; gap: 0.5rem; align-items: center; }
.loc-coord { color: #374151; font-size: 0.875rem; }
.loc-bar { background: #f3f4f6; height: 10px; border-radius: 999px; overflow: hidden; }
.loc-fill { height: 100%; }
.loc-fill.low { background: #bfdbfe; }
.loc-fill.med { background: #60a5fa; }
.loc-fill.high { background: #2563eb; }
.loc-count { font-weight: 600; color: #111827; }

.btn-secondary { padding: 0.5rem 1rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background: white; color: #374151; cursor: pointer; }
.select { padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.25rem; background: white; font-size: 0.875rem; }
</style>

