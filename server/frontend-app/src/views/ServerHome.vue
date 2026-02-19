<template>
  <div class="server-home">
    <h1>Detection Dashboard</h1>
    <p class="subtitle">แสดงผลการตรวจจับยานพาหนะจาก Edge AI Client ที่บันทึกลงฐานข้อมูล</p>
    <ServiceStatus />
    <p class="hint">ข้อมูลจาก DB จะแสดงเมื่อ Backend เชื่อมต่อ PostgreSQL และมี API สำหรับ cameras/detections</p>
  </div>
</template>

<script>
import ServiceStatus from '../components/ServiceStatus.vue'
export default {
  name: 'ServerHomePage',
  components: { ServiceStatus }
}
</script>

<style scoped>
.server-home { text-align: center; margin-top: 1rem; }
.subtitle { color: #6c757d; margin-bottom: 1rem; }
.hint { font-size: 0.85rem; color: #6c757d; margin-top: 1rem; }
</style>
