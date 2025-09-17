import { NestFactory } from '@nestjs/core';
import { SimpleAppModule } from './simple-app.module';
import * as fs from 'fs';

async function bootstrap() {
  const app = await NestFactory.create(SimpleAppModule);
  
  // Set global prefix for all routes
  app.setGlobalPrefix('api');
  
  // Enable CORS for frontend connections
  app.enableCors({
    origin: true, // Allow all origins in development
    credentials: true,
  });
  
  // Add a simple health check route
  app.use('/health', (req, res) => {
    res.json({ status: 'ok', message: 'AI Camera Server is running' });
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
