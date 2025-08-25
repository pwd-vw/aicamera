import { PrismaService } from '../database/prisma.service';
import { VisualizationService } from '../services/visualization.service';
import { AnalyticsEventService } from '../services/analytics-event.service';

// Example usage of the new Prisma models
export class PrismaUsageExample {
  constructor(
    private prisma: PrismaService,
    private visualizationService: VisualizationService,
    private analyticsEventService: AnalyticsEventService,
  ) {}

  async createSampleVisualizations() {
    // Create a chart visualization
    const chartViz = await this.visualizationService.create({
      name: 'Detection Trends Chart',
      description: 'Line chart showing detection trends over time',
      type: 'chart',
      configuration: {
        chartType: 'line',
        xAxis: 'timestamp',
        yAxis: 'detection_count',
        colors: ['#3B82F6'],
      },
      dataSource: 'detections_daily',
      refreshInterval: 300,
      createdBy: 'admin',
    });

    // Create a metric visualization
    const metricViz = await this.visualizationService.create({
      name: 'Total Detections',
      description: 'Real-time total detection count',
      type: 'metric',
      configuration: {
        format: 'number',
        prefix: '',
        suffix: ' detections',
        color: '#10B981',
      },
      dataSource: 'detections_total',
      refreshInterval: 60,
      createdBy: 'admin',
    });

    // Create a map visualization
    const mapViz = await this.visualizationService.create({
      name: 'Camera Locations Map',
      description: 'Interactive map showing camera locations',
      type: 'map',
      configuration: {
        center: { lat: 40.7128, lng: -74.0060 },
        zoom: 12,
        markers: 'camera_locations',
      },
      dataSource: 'cameras',
      refreshInterval: 600,
      createdBy: 'admin',
    });

    return { chartViz, metricViz, mapViz };
  }

  async createSampleAnalyticsEvents() {
    // Create user interaction events
    await this.analyticsEventService.create({
      eventType: 'visualization_viewed',
      eventCategory: 'user_interaction',
      userId: 'user123',
      sessionId: 'session456',
      visualizationId: 'viz789',
      eventData: {
        duration: 45,
        interactions: ['zoom', 'pan', 'filter'],
      },
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    });

    // Create system performance events
    await this.analyticsEventService.create({
      eventType: 'detection_processed',
      eventCategory: 'performance',
      cameraId: 'cam-001',
      eventData: {
        processingTime: 150,
        confidence: 0.95,
        imageSize: '2.3MB',
      },
    });

    // Create error events
    await this.analyticsEventService.create({
      eventType: 'camera_connection_failed',
      eventCategory: 'error',
      cameraId: 'cam-002',
      eventData: {
        errorCode: 'CONNECTION_TIMEOUT',
        retryAttempts: 3,
        lastSuccessfulConnection: '2024-01-15T10:30:00Z',
      },
    });

    // Create security events
    await this.analyticsEventService.create({
      eventType: 'unauthorized_access_attempt',
      eventCategory: 'security',
      userId: 'unknown',
      ipAddress: '203.0.113.1',
      eventData: {
        endpoint: '/api/admin/users',
        method: 'POST',
        userAgent: 'curl/7.68.0',
      },
    });
  }

  async getAnalyticsStats() {
    // Get event statistics for the last 24 hours
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const stats = await this.analyticsEventService.getEventStats({
      startDate: yesterday,
      endDate: new Date(),
    });

    console.log('Analytics Statistics (Last 24 hours):');
    console.log(`Total Events: ${stats.totalEvents}`);
    console.log('Events by Category:', stats.eventsByCategory);
    console.log('Events by Type:', stats.eventsByType);

    return stats;
  }

  async getActiveVisualizations() {
    const visualizations = await this.visualizationService.getActiveVisualizations();
    
    console.log('Active Visualizations:');
    visualizations.forEach(viz => {
      console.log(`- ${viz.name} (${viz.type}): ${viz.description}`);
    });

    return visualizations;
  }

  async runExample() {
    try {
      console.log('Creating sample visualizations...');
      const visualizations = await this.createSampleVisualizations();
      
      console.log('Creating sample analytics events...');
      await this.createSampleAnalyticsEvents();
      
      console.log('Getting analytics statistics...');
      await this.getAnalyticsStats();
      
      console.log('Getting active visualizations...');
      await this.getActiveVisualizations();
      
      console.log('Example completed successfully!');
    } catch (error) {
      console.error('Error running example:', error);
    }
  }
}
