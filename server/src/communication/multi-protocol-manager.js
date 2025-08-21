const logger = require('../utils/logger');
const WebSocket = require('ws');
const mqtt = require('mqtt');
const axios = require('axios');

/**
 * Multi-Protocol Communication Manager
 * Handles WebSocket (primary), REST API (backup), and MQTT (fallback) communication
 */
class MultiProtocolManager {
  constructor(config) {
    this.config = {
      websocket: {
        port: config.websocket?.port || 3001,
        path: config.websocket?.path || '/ws'
      },
      mqtt: {
        broker: config.mqtt?.broker || 'mqtt://localhost:1883',
        clientId: config.mqtt?.clientId || 'aicamera-server',
        username: config.mqtt?.username,
        password: config.mqtt?.password
      },
      rest: {
        baseUrl: config.rest?.baseUrl || 'http://localhost:3000/api/v1',
        timeout: config.rest?.timeout || 30000
      }
    };

    this.connections = {
      websocket: null,
      mqtt: null,
      rest: null
    };

    this.status = {
      websocket: 'disconnected',
      mqtt: 'disconnected',
      rest: 'available'
    };

    this.messageQueue = [];
    this.retryCounts = {
      websocket: 0,
      mqtt: 0,
      rest: 0
    };

    this.maxRetries = 3;
    this.retryDelays = {
      websocket: 5000,
      mqtt: 10000,
      rest: 3000
    };

    this.init();
  }

  /**
   * Initialize all communication protocols
   */
  async init() {
    try {
      // Initialize WebSocket server
      await this.initWebSocket();
      
      // Initialize MQTT client
      await this.initMQTT();
      
      // REST API is always available (no connection needed)
      this.status.rest = 'available';
      
      logger.info('Multi-protocol communication manager initialized');
    } catch (error) {
      logger.error('Failed to initialize communication manager:', error);
    }
  }

  /**
   * Initialize WebSocket server
   */
  async initWebSocket() {
    try {
      this.connections.websocket = new WebSocket.Server({
        port: this.config.websocket.port,
        path: this.config.websocket.path
      });

      this.connections.websocket.on('connection', (ws, req) => {
        logger.info('WebSocket client connected', { 
          remoteAddress: req.socket.remoteAddress,
          userAgent: req.headers['user-agent']
        });

        this.status.websocket = 'connected';
        this.retryCounts.websocket = 0;

        ws.on('message', (data) => {
          this.handleWebSocketMessage(ws, data);
        });

        ws.on('close', () => {
          logger.info('WebSocket client disconnected');
          this.status.websocket = 'disconnected';
          this.scheduleWebSocketRetry();
        });

        ws.on('error', (error) => {
          logger.error('WebSocket error:', error);
          this.status.websocket = 'error';
        });
      });

      this.connections.websocket.on('error', (error) => {
        logger.error('WebSocket server error:', error);
        this.status.websocket = 'error';
        this.scheduleWebSocketRetry();
      });

      logger.info('WebSocket server started on port', this.config.websocket.port);
    } catch (error) {
      logger.error('Failed to initialize WebSocket server:', error);
      this.status.websocket = 'error';
    }
  }

  /**
   * Initialize MQTT client
   */
  async initMQTT() {
    try {
      const options = {
        clientId: this.config.mqtt.clientId,
        clean: true,
        reconnectPeriod: 5000,
        connectTimeout: 30000
      };

      if (this.config.mqtt.username) {
        options.username = this.config.mqtt.username;
        options.password = this.config.mqtt.password;
      }

      this.connections.mqtt = mqtt.connect(this.config.mqtt.broker, options);

      this.connections.mqtt.on('connect', () => {
        logger.info('MQTT client connected');
        this.status.mqtt = 'connected';
        this.retryCounts.mqtt = 0;

        // Subscribe to relevant topics
        this.connections.mqtt.subscribe('aicamera/+/detection');
        this.connections.mqtt.subscribe('aicamera/+/status');
        this.connections.mqtt.subscribe('aicamera/+/alert');
      });

      this.connections.mqtt.on('message', (topic, message) => {
        this.handleMQTTMessage(topic, message);
      });

      this.connections.mqtt.on('disconnect', () => {
        logger.info('MQTT client disconnected');
        this.status.mqtt = 'disconnected';
        this.scheduleMQTTRetry();
      });

      this.connections.mqtt.on('error', (error) => {
        logger.error('MQTT error:', error);
        this.status.mqtt = 'error';
      });

    } catch (error) {
      logger.error('Failed to initialize MQTT client:', error);
      this.status.mqtt = 'error';
    }
  }

  /**
   * Send message using the best available protocol
   */
  async sendMessage(message, priority = 'normal') {
    const protocols = this.getProtocolsForPriority(priority);
    
    for (const protocol of protocols) {
      try {
        const success = await this.sendViaProtocol(protocol, message);
        if (success) {
          logger.debug('Message sent successfully via', protocol);
          return true;
        }
      } catch (error) {
        logger.warn(`Failed to send message via ${protocol}:`, error.message);
        continue;
      }
    }

    // If all protocols fail, queue the message
    this.queueMessage(message, priority);
    logger.warn('All communication protocols failed, message queued');
    return false;
  }

  /**
   * Send message via specific protocol
   */
  async sendViaProtocol(protocol, message) {
    switch (protocol) {
      case 'websocket':
        return this.sendViaWebSocket(message);
      case 'rest_api':
        return this.sendViaREST(message);
      case 'mqtt':
        return this.sendViaMQTT(message);
      default:
        throw new Error(`Unknown protocol: ${protocol}`);
    }
  }

  /**
   * Send message via WebSocket
   */
  sendViaWebSocket(message) {
    return new Promise((resolve, reject) => {
      if (this.status.websocket !== 'connected' || !this.connections.websocket) {
        reject(new Error('WebSocket not connected'));
        return;
      }

      this.connections.websocket.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          try {
            client.send(JSON.stringify(message));
            resolve(true);
          } catch (error) {
            reject(error);
          }
        }
      });

      // If no clients connected, reject
      if (this.connections.websocket.clients.size === 0) {
        reject(new Error('No WebSocket clients connected'));
      }
    });
  }

  /**
   * Send message via REST API
   */
  async sendViaREST(message) {
    try {
      const response = await axios.post(
        `${this.config.rest.baseUrl}/detection`,
        message,
        {
          timeout: this.config.rest.timeout,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      return response.status >= 200 && response.status < 300;
    } catch (error) {
      throw new Error(`REST API error: ${error.message}`);
    }
  }

  /**
   * Send message via MQTT
   */
  sendViaMQTT(message) {
    return new Promise((resolve, reject) => {
      if (this.status.mqtt !== 'connected' || !this.connections.mqtt) {
        reject(new Error('MQTT not connected'));
        return;
      }

      const topic = `aicamera/${message.camera_id || 'unknown'}/detection`;
      const payload = JSON.stringify(message);

      this.connections.mqtt.publish(topic, payload, { qos: 1 }, (error) => {
        if (error) {
          reject(error);
        } else {
          resolve(true);
        }
      });
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleWebSocketMessage(ws, data) {
    try {
      const message = JSON.parse(data);
      logger.info('Received WebSocket message:', message);
      
      // Process the message based on type
      this.processMessage(message, 'websocket');
    } catch (error) {
      logger.error('Error processing WebSocket message:', error);
    }
  }

  /**
   * Handle incoming MQTT messages
   */
  handleMQTTMessage(topic, message) {
    try {
      const data = JSON.parse(message.toString());
      logger.info('Received MQTT message:', { topic, data });
      
      // Process the message based on topic and data
      this.processMessage(data, 'mqtt', topic);
    } catch (error) {
      logger.error('Error processing MQTT message:', error);
    }
  }

  /**
   * Process incoming messages
   */
  processMessage(message, source, topic = null) {
    // Handle different message types
    switch (message.type) {
      case 'detection':
        this.handleDetectionMessage(message, source);
        break;
      case 'status':
        this.handleStatusMessage(message, source);
        break;
      case 'alert':
        this.handleAlertMessage(message, source);
        break;
      default:
        logger.warn('Unknown message type:', message.type);
    }
  }

  /**
   * Handle detection messages
   */
  handleDetectionMessage(message, source) {
    logger.info('Processing detection message from', source, message);
    // TODO: Process detection data
    // - Save to database
    // - Trigger analytics
    // - Send notifications
  }

  /**
   * Handle status messages
   */
  handleStatusMessage(message, source) {
    logger.info('Processing status message from', source, message);
    // TODO: Update camera status
    // - Update database
    // - Broadcast to dashboard
  }

  /**
   * Handle alert messages
   */
  handleAlertMessage(message, source) {
    logger.warn('Processing alert message from', source, message);
    // TODO: Handle alerts
    // - Send notifications
    // - Log critical events
    // - Trigger actions
  }

  /**
   * Get protocols for message priority
   */
  getProtocolsForPriority(priority) {
    const protocolMap = {
      critical: ['websocket', 'rest_api', 'mqtt'],
      high: ['websocket', 'rest_api'],
      normal: ['websocket', 'rest_api'],
      low: ['rest_api']
    };
    return protocolMap[priority] || protocolMap.normal;
  }

  /**
   * Queue message for later delivery
   */
  queueMessage(message, priority) {
    this.messageQueue.push({
      message,
      priority,
      timestamp: new Date(),
      attempts: 0
    });
    
    // Process queue periodically
    this.processMessageQueue();
  }

  /**
   * Process queued messages
   */
  async processMessageQueue() {
    if (this.messageQueue.length === 0) return;

    const availableProtocols = this.getAvailableProtocols();
    if (availableProtocols.length === 0) return;

    const messagesToProcess = this.messageQueue.splice(0, 10); // Process 10 at a time

    for (const queuedMessage of messagesToProcess) {
      try {
        const success = await this.sendMessage(queuedMessage.message, queuedMessage.priority);
        if (success) {
          logger.info('Queued message sent successfully');
        } else {
          queuedMessage.attempts++;
          if (queuedMessage.attempts < this.maxRetries) {
            this.messageQueue.push(queuedMessage);
          } else {
            logger.error('Message failed after max retries:', queuedMessage);
          }
        }
      } catch (error) {
        logger.error('Error processing queued message:', error);
      }
    }
  }

  /**
   * Get available protocols
   */
  getAvailableProtocols() {
    const available = [];
    if (this.status.websocket === 'connected') available.push('websocket');
    if (this.status.rest === 'available') available.push('rest_api');
    if (this.status.mqtt === 'connected') available.push('mqtt');
    return available;
  }

  /**
   * Schedule WebSocket retry
   */
  scheduleWebSocketRetry() {
    if (this.retryCounts.websocket < this.maxRetries) {
      setTimeout(() => {
        this.retryCounts.websocket++;
        this.initWebSocket();
      }, this.retryDelays.websocket * this.retryCounts.websocket);
    }
  }

  /**
   * Schedule MQTT retry
   */
  scheduleMQTTRetry() {
    if (this.retryCounts.mqtt < this.maxRetries) {
      setTimeout(() => {
        this.retryCounts.mqtt++;
        this.initMQTT();
      }, this.retryDelays.mqtt * this.retryCounts.mqtt);
    }
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      ...this.status,
      queueSize: this.messageQueue.length,
      availableProtocols: this.getAvailableProtocols()
    };
  }

  /**
   * Close all connections
   */
  async close() {
    logger.info('Closing multi-protocol communication manager...');
    
    if (this.connections.websocket) {
      this.connections.websocket.close();
    }
    
    if (this.connections.mqtt) {
      this.connections.mqtt.end();
    }
    
    logger.info('Multi-protocol communication manager closed');
  }
}

module.exports = MultiProtocolManager;
