<template>
  <div class="server-home">
    <h1>Detection Dashboard</h1>
    <p class="subtitle">แสดงผลการตรวจจับยานพาหนะจาก Edge AI Client ที่บันทึกลงฐานข้อมูล</p>
    <ServiceStatus />

    <div class="db-section">
      <h2>Images (จาก Detections)</h2>
      <p v-if="detectionsWithImage.length === 0 && !loading.detections" class="hint">ไม่มีภาพที่บันทึกใน detections</p>
      <p v-else-if="loading.detections" class="hint">กำลังโหลด...</p>
      <div v-else class="image-grid">
        <div v-for="d in detectionsWithImage" :key="d.id" class="image-card">
          <img
            :src="apiUrl('/detections/' + d.id + '/image')"
            :alt="'Detection ' + d.id"
            loading="lazy"
            @error="onImageError"
          />
          <div class="image-label">{{ d.licensePlate || d.id }} ({{ formatDate(d.timestamp) }})</div>
        </div>
      </div>
    </div>

    <div v-for="table in tableConfig" :key="table.key" class="db-section">
      <h2>{{ table.title }}</h2>
      <p v-if="loading[table.key]" class="hint">กำลังโหลด...</p>
      <p v-else-if="errors[table.key]" class="error-msg">{{ errors[table.key] }}</p>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="col in tableColumns(table.key)" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in tableRows(table.key)" :key="row.id || idx">
              <td v-for="col in tableColumns(table.key)" :key="col" class="cell">
                <template v-if="col === '_image_link' && row.imagePath && row.id">
                  <a :href="apiUrl('/detections/' + row.id + '/image')" target="_blank" rel="noopener">ดูภาพ</a>
                </template>
                <template v-else>
                  {{ formatCell(row[col]) }}
                </template>
              </td>
            </tr>
            <tr v-if="tableRows(table.key).length === 0">
              <td :colspan="tableColumns(table.key).length" class="empty">ไม่มีข้อมูล</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import ServiceStatus from '../components/ServiceStatus.vue'

export default {
  name: 'ServerHomePage',
  components: { ServiceStatus },
  data () {
    return {
      apiBase: typeof window !== 'undefined' ? window.location.origin + '/server/api' : '',
      cameras: [],
      detections: [],
      cameraHealth: [],
      analytics: [],
      systemEvents: [],
      visualizations: [],
      analyticsEvents: [],
      loading: {
        cameras: true,
        detections: true,
        cameraHealth: true,
        analytics: true,
        systemEvents: true,
        visualizations: true,
        analyticsEvents: true
      },
      errors: {},
      tableConfig: [
        { key: 'cameras', title: 'Cameras', endpoint: '/cameras' },
        { key: 'detections', title: 'Detections', endpoint: '/detections' },
        { key: 'cameraHealth', title: 'Camera Health', endpoint: '/camera-health' },
        { key: 'analytics', title: 'Analytics', endpoint: '/analytics' },
        { key: 'systemEvents', title: 'System Events', endpoint: '/system-events' },
        { key: 'visualizations', title: 'Visualizations', endpoint: '/visualizations' },
        { key: 'analyticsEvents', title: 'Analytics Events', endpoint: '/analytics-events' }
      ],
      // Fallback column headers when table has no rows (for UI layout and design)
      fallbackColumns: {
        cameras: ['id', 'cameraId', 'name', 'locationLat', 'locationLng', 'locationAddress', 'status', 'detectionEnabled', 'imageQuality', 'uploadInterval', 'configuration', 'createdAt', 'updatedAt'],
        detections: ['id', 'cameraId', 'timestamp', 'licensePlate', 'confidence', 'imageUrl', 'imagePath', 'status', 'metadata', 'createdAt', 'updatedAt', '_image_link'],
        cameraHealth: ['id', 'cameraId', 'timestamp', 'status', 'cpuUsage', 'memoryUsage', 'diskUsage', 'temperature', 'uptimeSeconds', 'lastDetectionAt', 'metadata', 'createdAt'],
        analytics: ['id', 'cameraId', 'date', 'totalDetections', 'uniquePlates', 'averageConfidence', 'createdAt', 'updatedAt'],
        systemEvents: ['id', 'cameraId', 'eventType', 'eventLevel', 'message', 'metadata', 'createdAt'],
        visualizations: ['id', 'name', 'description', 'type', 'configuration', 'dataSource', 'refreshInterval', 'isActive', 'createdBy', 'createdAt', 'updatedAt'],
        analyticsEvents: ['id', 'eventType', 'eventCategory', 'userId', 'sessionId', 'cameraId', 'visualizationId', 'eventData', 'ipAddress', 'userAgent', 'createdAt']
      }
    }
  },
  computed: {
    detectionsWithImage () {
      return (this.detections || []).filter(d => d.imagePath)
    }
  },
  mounted () {
    this.tableConfig.forEach(t => this.fetchTable(t.key, t.endpoint))
  },
  methods: {
    apiUrl (path) {
      return this.apiBase + path
    },
    async fetchTable (key, endpoint) {
      this.loading[key] = true
      this.errors[key] = null
      try {
        const res = await fetch(this.apiUrl(endpoint + '?limit=500'))
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        this[key] = Array.isArray(data) ? data : []
      } catch (e) {
        this.errors[key] = e.message || 'โหลดไม่สำเร็จ'
        this[key] = []
      } finally {
        this.loading[key] = false
      }
    },
    tableColumns (key) {
      const rows = this[key]
      if (!rows || rows.length === 0) {
        return this.fallbackColumns[key] || []
      }
      const first = rows[0]
      let cols = Object.keys(first)
      if (key === 'detections' && rows.some(r => r.imagePath)) {
        cols = cols.filter(c => c !== 'imagePath').concat(['_image_link'])
      }
      return cols
    },
    tableRows (key) {
      const rows = this[key]
      if (!rows) return []
      return rows.map(r => {
        const out = { ...r }
        if (key === 'detections' && r.imagePath) out._image_link = true
        return out
      })
    },
    formatCell (val) {
      if (val == null) return ''
      if (typeof val === 'object') return JSON.stringify(val).slice(0, 120) + (JSON.stringify(val).length > 120 ? '…' : '')
      return String(val)
    },
    formatDate (val) {
      if (!val) return ''
      try {
        const d = new Date(val)
        return isNaN(d.getTime()) ? val : d.toLocaleString()
      } catch {
        return val
      }
    },
    onImageError (e) {
      e.target.style.display = 'none'
    }
  }
}
</script>

<style scoped>
.server-home { text-align: left; margin-top: 1rem; max-width: 100%; padding: 0 1rem; }
.subtitle { color: #6c757d; margin-bottom: 1rem; }
.db-section { margin: 2rem 0; }
.db-section h2 { font-size: 1.15rem; margin-bottom: 0.75rem; color: #333; border-bottom: 1px solid #dee2e6; padding-bottom: 0.25rem; }
.hint { font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0; }
.error-msg { color: #dc3545; font-size: 0.9rem; }
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.data-table th, .data-table td { border: 1px solid #dee2e6; padding: 0.4rem 0.6rem; text-align: left; }
.data-table th { background: #f8f9fa; font-weight: 600; }
.data-table .cell { max-width: 280px; overflow: hidden; text-overflow: ellipsis; }
.data-table .empty { color: #6c757d; font-style: italic; text-align: center; }
.data-table a { color: #0d6efd; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.image-card { border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; background: #f8f9fa; }
.image-card img { width: 100%; height: auto; display: block; min-height: 80px; }
.image-label { padding: 0.35rem 0.5rem; font-size: 0.8rem; color: #495057; }
</style>
