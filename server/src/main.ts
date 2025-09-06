import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as fs from 'fs';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import { createValidationPipe } from './config/validation.config';
import { ValidationInterceptor } from './interceptors/validation.interceptor';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.setGlobalPrefix('api/v1');
  app.useGlobalPipes(createValidationPipe());
  app.useGlobalInterceptors(new ValidationInterceptor());
  
  app.use(helmet());
  app.use(compression());
  app.use(morgan('combined'));
  
  // Enable CORS for frontend connections
  app.enableCors({
    origin: true, // Allow all origins in development
    credentials: true,
  });
  
  // Check if Unix socket should be used
  const socketPath = process.env.UNIX_SOCKET;
  
  if (socketPath) {
    // Remove existing socket file if it exists
    if (fs.existsSync(socketPath)) {
      fs.unlinkSync(socketPath);
    }
    
    await app.listen(socketPath);
    
    // Set socket permissions for nginx access
    fs.chmodSync(socketPath, 0o666);
    
    console.log(`Application is running on Unix socket: ${socketPath}`);
  } else {
    // Fall back to TCP port
    const port = process.env.PORT || 3000;
    await app.listen(port);
    console.log(`Application is running on: http://localhost:${port}`);
  }
}

bootstrap();
