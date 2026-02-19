<template>
  <div class="network">
    <h1>Communication Network</h1>
    <p class="subtitle">สถานะ Microservice ที่ใช้สื่อสารกับ Edge Client – Server และข้อมูลสำหรับการ Config Client</p>
    <ServiceStatus />
    <section class="client-info">
      <h2>การเชื่อมต่อสำหรับลูกข่าย (Client)</h2>
      <ul>
        <li><strong>WebSocket (Socket.IO)</strong>: URL <code>http://lprserver.tail605477.ts.net/ws/</code> — path <code>/ws/</code>, port 80 เท่านั้น</li>
        <li><strong>REST API</strong>: <code>/server/api/</code> — proxy ไป Backend port 3000</li>
        <li><strong>MQTT</strong>: Broker ที่ port 1883 (เช่น <code>mqtt://lprserver.tail605477.ts.net:1883</code>) — topics ตาม MQTT_CLIENT_GUIDE</li>
      </ul>
    </section>
  </div>
</template>

<script>
import ServiceStatus from '../components/ServiceStatus.vue'
export default {
  name: 'NetworkPage',
  components: { ServiceStatus }
}
</script>

<style scoped>
.network { text-align: left; max-width: 720px; margin: 1rem auto; padding: 0 1rem; }
.subtitle { color: #6c757d; margin-bottom: 1.5rem; }
.client-info { margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; }
.client-info h2 { font-size: 1rem; margin: 0 0 0.75rem 0; }
.client-info ul { margin: 0; padding-left: 1.25rem; }
.client-info code { background: #e9ecef; padding: 0.1em 0.4em; border-radius: 4px; font-size: 0.9em; }
</style>
