# Prisma Setup and Usage

This document describes the Prisma ORM setup for the AI Camera server component.

## Overview

The project has been migrated from raw SQL to Prisma ORM for better type safety, developer experience, and database management.

## Installation

Prisma has been installed with the following packages:
- `prisma`: Prisma CLI and core functionality
- `@prisma/client`: Generated Prisma client for database operations

## Database Schema

The Prisma schema (`prisma/schema.prisma`) includes the following models:

### Core Models
- **Camera**: Edge camera devices that perform LPR detection
- **Detection**: License plate detection results from edge cameras
- **Analytics**: Daily aggregated analytics data
- **CameraHealth**: Camera health monitoring data
- **SystemEvent**: System events and logs

### New Models
- **Visualization**: Dashboard charts and graphs configuration
- **AnalyticsEvent**: User interactions and system events for analytics

### Enums
- `CameraStatus`: active, inactive, maintenance
- `DetectionStatus`: pending, processed, failed
- `ImageQuality`: low, medium, high
- `VisualizationType`: chart, graph, table, metric, map
- `AnalyticsEventCategory`: user_interaction, system_event, performance, error, security

## Services

### PrismaService
Core database service that manages Prisma client lifecycle:
- Connection management
- Database cleanup (development only)
- Proper shutdown handling

### VisualizationService
Handles visualization operations:
- CRUD operations for visualizations
- Filtering by type and active status
- Configuration management

### AnalyticsEventService
Handles analytics event operations:
- Event creation and retrieval
- Statistics and reporting
- Event categorization and filtering

## Controllers

### VisualizationController
REST API endpoints for visualization management:
- `POST /visualizations` - Create visualization
- `GET /visualizations` - List visualizations with filters
- `GET /visualizations/active` - Get active visualizations
- `GET /visualizations/type/:type` - Get visualizations by type
- `GET /visualizations/:id` - Get specific visualization
- `PUT /visualizations/:id` - Update visualization
- `DELETE /visualizations/:id` - Delete visualization

### AnalyticsEventController
REST API endpoints for analytics events:
- `POST /analytics-events` - Create analytics event
- `GET /analytics-events` - List events with filters
- `GET /analytics-events/stats` - Get event statistics
- `GET /analytics-events/category/:category` - Get events by category
- `GET /analytics-events/user/:userId` - Get events by user
- `GET /analytics-events/camera/:cameraId` - Get events by camera
- `GET /analytics-events/visualization/:visualizationId` - Get events by visualization
- `GET /analytics-events/:id` - Get specific event

## Usage Examples

### Creating a Visualization
```typescript
const visualization = await visualizationService.create({
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
```

### Creating an Analytics Event
```typescript
const event = await analyticsEventService.create({
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
  userAgent: 'Mozilla/5.0...',
});
```

### Getting Event Statistics
```typescript
const stats = await analyticsEventService.getEventStats({
  startDate: new Date('2024-01-01'),
  endDate: new Date('2024-01-31'),
});

console.log(`Total Events: ${stats.totalEvents}`);
console.log('Events by Category:', stats.eventsByCategory);
console.log('Events by Type:', stats.eventsByType);
```

## Database Commands

### Generate Prisma Client
```bash
npx prisma generate
```

### Push Schema to Database
```bash
npx prisma db push
```

### Create Migration
```bash
npx prisma migrate dev --name migration_name
```

### Reset Database (Development)
```bash
npx prisma migrate reset
```

### View Database in Prisma Studio
```bash
npx prisma studio
```

## Environment Variables

Make sure your `.env` file contains:
```
DATABASE_URL="postgresql://username:password@localhost:5432/aicamera_db"
```

## Type Safety

All database operations are fully typed. The generated Prisma client provides:
- Type-safe queries
- Auto-completion
- Compile-time error checking
- Relationship handling

## Best Practices

1. **Use Services**: Always use the service layer for database operations
2. **Error Handling**: Implement proper error handling for database operations
3. **Transactions**: Use Prisma transactions for complex operations
4. **Relationships**: Leverage Prisma's relationship features for efficient queries
5. **Indexing**: Ensure proper database indexing for performance
6. **Validation**: Validate input data before database operations

## Migration from SQL

The existing SQL schema has been converted to Prisma format with:
- Proper field mappings
- Relationship definitions
- Enum types
- Indexes and constraints
- Triggers and functions (handled by Prisma)

## Next Steps

1. Update existing services to use Prisma instead of raw SQL
2. Add validation using class-validator
3. Implement caching strategies
4. Add database connection pooling
5. Set up automated testing with Prisma
