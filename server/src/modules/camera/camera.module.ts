import { Module } from '@nestjs/common';
import { CameraController } from './camera.controller';

@Module({
  controllers: [CameraController],
})
export class CameraModule {}

