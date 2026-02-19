<template>
  <div class="edge-control">
    <h1>Edge AI Dashboard</h1>
    <p class="subtitle">แสดงผลข้อมูลจาก Edge Client Device แต่ละตัว (สถานะแบตเตอรี่, ดิสก์, CPU, RAM, อุณหภูมิ, uptime, พิกัด, สถานะเครือข่าย) จาก log ที่ส่งผ่าน MQTT</p>
    <section class="placeholder">
      <p>Dashboard จะแสดงรายการอุปกรณ์และสถานะเมื่อมีข้อมูลจาก MQTT topics <code>camera/+/health</code>, <code>camera/+/status</code> และ backend API พร้อมให้บริการ</p>
    </section>
  </div>
</template>

<script>
export default {
  name: 'EdgeControlPage'
}
</script>

<style scoped>
.edge-control { text-align: left; max-width: 720px; margin: 1rem auto; padding: 0 1rem; }
.subtitle { color: #6c757d; margin-bottom: 1.5rem; }
.placeholder { padding: 1.5rem; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; }
.placeholder code { background: #e9ecef; padding: 0.1em 0.4em; border-radius: 4px; }
</style>
