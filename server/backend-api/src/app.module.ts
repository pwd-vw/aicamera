import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { DeviceModule } from './device/device.module';
import { Camera, Detection, Analytics, CameraHealth, SystemEvent, Visualization, AnalyticsEvent } from './entities';

const databaseUrl =
  process.env.DATABASE_URL ||
  (process.env.POSTGRES_HOST
    ? `postgresql://${process.env.POSTGRES_USER || 'postgres'}:${process.env.POSTGRES_PASSWORD || ''}@${process.env.POSTGRES_HOST}:${process.env.POSTGRES_PORT || 5432}/${process.env.POSTGRES_DB || 'aicamera'}`
    : 'postgresql://postgres:postgres@localhost:5432/aicamera');

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'postgres',
      url: databaseUrl,
      entities: [Camera, Detection, Analytics, CameraHealth, SystemEvent, Visualization, AnalyticsEvent],
      synchronize: false,
      logging: process.env.NODE_ENV === 'development',
    }),
    AuthModule,
    DeviceModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
