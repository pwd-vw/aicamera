const express = require('express');
const router = express.Router();

// Import route modules
const detectionRoutes = require('./detection');
const cameraRoutes = require('./camera');
const analyticsRoutes = require('./analytics');
const healthRoutes = require('./health');

// API version info
router.get('/', (req, res) => {
  res.json({
    message: 'AI Camera Server API v1',
    version: '1.0.0',
    endpoints: {
      detection: '/detection',
      camera: '/camera',
      analytics: '/analytics',
      health: '/health'
    }
  });
});

// Mount route modules
router.use('/detection', detectionRoutes);
router.use('/camera', cameraRoutes);
router.use('/analytics', analyticsRoutes);
router.use('/health', healthRoutes);

module.exports = router;
