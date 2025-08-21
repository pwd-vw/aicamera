const logger = require('../utils/logger');

/**
 * Socket.IO connection handler
 * Handles real-time communication with edge cameras
 */
function socketHandler(io) {
  io.on('connection', (socket) => {
    logger.info('New socket connection', { id: socket.id });

    // Handle camera registration
    socket.on('camera:register', (data) => {
      try {
        logger.info('Camera registration request', {
          socketId: socket.id,
          cameraId: data.camera_id,
          location: data.location
        });

        // Join camera-specific room
        socket.join(`camera:${data.camera_id}`);
        
        // Store camera info in socket
        socket.cameraId = data.camera_id;
        socket.cameraInfo = data;

        // Acknowledge registration
        socket.emit('camera:registered', {
          success: true,
          message: 'Camera registered successfully',
          camera_id: data.camera_id
        });

        // Notify other clients about new camera
        socket.broadcast.emit('camera:connected', {
          camera_id: data.camera_id,
          location: data.location,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error('Error in camera registration:', error);
        socket.emit('camera:registration_error', {
          success: false,
          error: 'Registration failed'
        });
      }
    });

    // Handle real-time detection data
    socket.on('detection:data', (data) => {
      try {
        logger.info('Received real-time detection data', {
          socketId: socket.id,
          cameraId: socket.cameraId,
          licensePlate: data.license_plate,
          confidence: data.confidence
        });

        // TODO: Process and store detection data
        // TODO: Trigger analytics updates
        // TODO: Send notifications if needed

        // Broadcast to dashboard clients
        socket.broadcast.emit('detection:new', {
          camera_id: socket.cameraId,
          detection: data,
          timestamp: new Date().toISOString()
        });

        // Acknowledge receipt
        socket.emit('detection:received', {
          success: true,
          message: 'Detection data received'
        });

      } catch (error) {
        logger.error('Error processing detection data:', error);
        socket.emit('detection:error', {
          success: false,
          error: 'Failed to process detection data'
        });
      }
    });

    // Handle camera status updates
    socket.on('camera:status', (data) => {
      try {
        logger.info('Camera status update', {
          socketId: socket.id,
          cameraId: socket.cameraId,
          status: data.status
        });

        // Broadcast status update
        socket.broadcast.emit('camera:status_update', {
          camera_id: socket.cameraId,
          status: data.status,
          timestamp: new Date().toISOString()
        });

      } catch (error) {
        logger.error('Error processing status update:', error);
      }
    });

    // Handle dashboard client connection
    socket.on('dashboard:connect', (data) => {
      try {
        logger.info('Dashboard client connected', {
          socketId: socket.id,
          clientType: 'dashboard'
        });

        // Join dashboard room
        socket.join('dashboard');
        socket.clientType = 'dashboard';

        // Send current system status
        socket.emit('dashboard:status', {
          cameras: [], // TODO: Get active cameras
          detections_today: 0, // TODO: Get today's detections
          system_status: 'operational'
        });

      } catch (error) {
        logger.error('Error in dashboard connection:', error);
      }
    });

    // Handle ping/pong for connection monitoring
    socket.on('ping', () => {
      socket.emit('pong', { timestamp: new Date().toISOString() });
    });

    // Handle disconnection
    socket.on('disconnect', (reason) => {
      logger.info('Socket disconnected', {
        socketId: socket.id,
        cameraId: socket.cameraId,
        clientType: socket.clientType,
        reason
      });

      // If it was a camera, notify other clients
      if (socket.cameraId) {
        socket.broadcast.emit('camera:disconnected', {
          camera_id: socket.cameraId,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Handle errors
    socket.on('error', (error) => {
      logger.error('Socket error:', error);
    });
  });

  // Global error handler
  io.on('error', (error) => {
    logger.error('Socket.IO error:', error);
  });

  return io;
}

module.exports = socketHandler;
