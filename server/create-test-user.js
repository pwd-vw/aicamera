const { PrismaClient } = require('./dist/generated/prisma');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function createTestUser() {
  try {
    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email: 'testuser@example.com' }
    });

    if (existingUser) {
      console.log('User already exists:', existingUser.email);
      return;
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash('testuser123', 10);

    // Create the user
    const user = await prisma.user.create({
      data: {
        email: 'testuser@example.com',
        username: 'testuser',
        password: hashedPassword,
        role: 'admin',
        isActive: true,
        firstName: 'Test',
        lastName: 'User'
      }
    });

    console.log('Test user created successfully:', {
      id: user.id,
      email: user.email,
      username: user.username,
      role: user.role
    });

  } catch (error) {
    console.error('Error creating test user:', error);
  } finally {
    await prisma.$disconnect();
  }
}

createTestUser();
