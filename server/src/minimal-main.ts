import { NestFactory } from '@nestjs/core';
import { MinimalAppModule } from './minimal-app.module';

async function bootstrap() {
  const app = await NestFactory.create(MinimalAppModule);
  
  // Set global prefix for all routes
  app.setGlobalPrefix('api');
  
  // Enable CORS for frontend connections
  app.enableCors({
    origin: true,
    credentials: true,
  });
  
  const port = process.env.PORT || 3000;
  await app.listen(port);
  console.log(`Minimal NestJS server running on: http://localhost:${port}`);
}

bootstrap();
