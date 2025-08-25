import { AuthService } from '../auth/auth.service';
import { UserService } from '../services/user.service';
import { UserRole } from '../../generated/prisma';

// Example usage of the JWT authentication system
export class AuthUsageExample {
  constructor(
    private authService: AuthService,
    private userService: UserService,
  ) {}

  async createSampleUsers() {
    try {
      // Create an admin user
      const admin = await this.authService.createAdminUser(
        'admin@aicamera.com',
        'admin',
        'admin123',
      );

      // Register a regular user
      const user = await this.authService.register({
        email: 'user@aicamera.com',
        username: 'user',
        password: 'user123',
        firstName: 'John',
        lastName: 'Doe',
        role: UserRole.operator,
      });

      // Register a viewer user
      const viewer = await this.authService.register({
        email: 'viewer@aicamera.com',
        username: 'viewer',
        password: 'viewer123',
        firstName: 'Jane',
        lastName: 'Smith',
        role: UserRole.viewer,
      });

      console.log('Sample users created:');
      console.log('- Admin:', admin.username);
      console.log('- Operator:', user.user.username);
      console.log('- Viewer:', viewer.user.username);

      return { admin, user, viewer };
    } catch (error) {
      console.error('Error creating sample users:', error);
      throw error;
    }
  }

  async demonstrateLogin() {
    try {
      // Login as admin
      const adminLogin = await this.authService.login({
        username: 'admin',
        password: 'admin123',
      });

      console.log('Admin login successful:');
      console.log('Access Token:', adminLogin.accessToken.substring(0, 50) + '...');
      console.log('User Role:', adminLogin.user.role);

      // Login as operator
      const operatorLogin = await this.authService.login({
        username: 'user',
        password: 'user123',
      });

      console.log('Operator login successful:');
      console.log('Access Token:', operatorLogin.accessToken.substring(0, 50) + '...');
      console.log('User Role:', operatorLogin.user.role);

      return { adminLogin, operatorLogin };
    } catch (error) {
      console.error('Error during login:', error);
      throw error;
    }
  }

  async demonstrateUserManagement() {
    try {
      // Get all users
      const allUsers = await this.userService.findAll();
      console.log('All users:', allUsers.length);

      // Get users by role
      const admins = await this.userService.getUsersByRole(UserRole.admin);
      const operators = await this.userService.getUsersByRole(UserRole.operator);
      const viewers = await this.userService.getUsersByRole(UserRole.viewer);

      console.log('Users by role:');
      console.log('- Admins:', admins.length);
      console.log('- Operators:', operators.length);
      console.log('- Viewers:', viewers.length);

      // Get user statistics
      const stats = await this.userService.getUserStats();
      console.log('User statistics:', stats);

      return { allUsers, admins, operators, viewers, stats };
    } catch (error) {
      console.error('Error in user management:', error);
      throw error;
    }
  }

  async demonstratePasswordChange() {
    try {
      // Find a user
      const user = await this.userService.findByUsername('user');
      if (!user) {
        throw new Error('User not found');
      }

      // Change password
      await this.authService.changePassword(user.id, {
        currentPassword: 'user123',
        newPassword: 'newuser123',
      });

      console.log('Password changed successfully');

      // Try to login with new password
      const newLogin = await this.authService.login({
        username: 'user',
        password: 'newuser123',
      });

      console.log('Login with new password successful');

      return newLogin;
    } catch (error) {
      console.error('Error changing password:', error);
      throw error;
    }
  }

  async demonstrateProfileUpdate() {
    try {
      // Find a user
      const user = await this.userService.findByUsername('viewer');
      if (!user) {
        throw new Error('User not found');
      }

      // Update profile
      const updatedUser = await this.authService.updateProfile(user.id, {
        firstName: 'Jane Updated',
        lastName: 'Smith Updated',
        email: 'viewer.updated@aicamera.com',
      });

      console.log('Profile updated successfully:');
      console.log('New name:', updatedUser.firstName, updatedUser.lastName);
      console.log('New email:', updatedUser.email);

      return updatedUser;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  async runExample() {
    try {
      console.log('=== JWT Authentication System Demo ===\n');

      console.log('1. Creating sample users...');
      await this.createSampleUsers();

      console.log('\n2. Demonstrating login...');
      await this.demonstrateLogin();

      console.log('\n3. Demonstrating user management...');
      await this.demonstrateUserManagement();

      console.log('\n4. Demonstrating password change...');
      await this.demonstratePasswordChange();

      console.log('\n5. Demonstrating profile update...');
      await this.demonstrateProfileUpdate();

      console.log('\n=== Demo completed successfully! ===');
    } catch (error) {
      console.error('Demo failed:', error);
    }
  }
}
