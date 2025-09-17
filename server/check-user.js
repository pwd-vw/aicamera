const { PrismaClient } = require('./dist/generated/prisma');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function checkUser() {
  try {
    console.log('Checking users in database...');
    
    const users = await prisma.user.findMany();
    console.log('All users:', users.map(u => ({ id: u.id, username: u.username, email: u.email, role: u.role, isActive: u.isActive })));
    
    const testUser = await prisma.user.findUnique({
      where: { username: 'testuser' }
    });
    
    if (testUser) {
      console.log('Test user found:', {
        id: testUser.id,
        username: testUser.username,
        email: testUser.email,
        role: testUser.role,
        isActive: testUser.isActive
      });
      
      // Test password
      const isValid = await bcrypt.compare('testuser123', testUser.password);
      console.log('Password testuser123 is valid:', isValid);
    } else {
      console.log('Test user not found');
    }
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

checkUser();
