const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('./dist/generated/prisma');

const app = express();
const prisma = new PrismaClient();

// Middleware
app.use(cors({
  origin: true,
  credentials: true,
}));
app.use(express.json());

// Auth routes
app.post('/api/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    // Find user
    const user = await prisma.user.findUnique({
      where: { username },
    });

    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { 
        id: user.id, 
        username: user.username, 
        role: user.role 
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '1h' }
    );

    const { password: _, ...userWithoutPassword } = user;

    res.json({
      accessToken: token,
      user: userWithoutPassword,
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/auth/profile', (req, res) => {
  res.json({ message: 'Profile endpoint' });
});

// Cameras routes
app.get('/api/cameras', async (req, res) => {
  try {
    const cameras = await prisma.camera.findMany({
      include: {
        detections: {
          take: 1,
          orderBy: { createdAt: 'desc' }
        }
      }
    });

    // Add detection count to each camera
    const camerasWithCounts = cameras.map(camera => ({
      ...camera,
      detectionCount: camera.detections.length
    }));

    res.json(camerasWithCounts);
  } catch (error) {
    console.error('Get cameras error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Detections routes
app.get('/api/detections', async (req, res) => {
  try {
    const { cameraId, limit = 10 } = req.query;
    
    const detections = await prisma.detection.findMany({
      where: cameraId ? { cameraId } : {},
      take: parseInt(limit),
      orderBy: { createdAt: 'desc' }
    });

    res.json(detections);
  } catch (error) {
    console.error('Get detections error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Simple server is running' });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({ message: 'AI Camera Server API', version: '1.0.0' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Simple server running on http://localhost:${PORT}`);
});
