const { PrismaClient } = require('./dist/generated/prisma');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function updateTestUser() {
  try {
    console.log('Updating test user password...');
    
    // Hash the new password
    const hashedPassword = await bcrypt.hash('testuser123', 10);
    
    // Update the test user
    const updatedUser = await prisma.user.update({
      where: { username: 'testuser' },
      data: { password: hashedPassword }
    });
    
    console.log('Test user updated successfully:', {
      id: updatedUser.id,
      username: updatedUser.username,
      email: updatedUser.email,
      role: updatedUser.role,
      isActive: updatedUser.isActive
    });
    
    // Test the password
    const isValid = await bcrypt.compare('testuser123', updatedUser.password);
    console.log('Password testuser123 is now valid:', isValid);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

updateTestUser();
