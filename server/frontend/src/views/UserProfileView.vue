<template>
  <div class="p-6">
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="btn-secondary">← Back</button>
        <h1 class="text-2xl font-semibold">User Profile</h1>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="auth.user">{{ auth.user.username }} ({{ auth.user.role }})</span>
        <router-link to="/users" class="btn-secondary" v-if="auth.user?.role === 'admin'">User Management</router-link>
        <button class="btn" @click="onLogout">Logout</button>
      </div>
    </header>

    <div class="space-y-6">
      <!-- Profile Information -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Profile Information</h2>
        <form @submit.prevent="updateProfile" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Username</label>
              <input v-model="profile.username" class="input" readonly />
            </div>
            <div>
              <label class="label">Email</label>
              <input v-model="profile.email" type="email" class="input" required />
            </div>
            <div>
              <label class="label">First Name</label>
              <input v-model="profile.firstName" class="input" />
            </div>
            <div>
              <label class="label">Last Name</label>
              <input v-model="profile.lastName" class="input" />
            </div>
            <div>
              <label class="label">Role</label>
              <input :value="profile.role" class="input" readonly />
            </div>
            <div>
              <label class="label">Account Status</label>
              <span :class="profile.isActive ? 'badge-active' : 'badge-inactive'">
                {{ profile.isActive ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          <button type="submit" class="btn" :disabled="loadingUpdate">
            {{ loadingUpdate ? 'Updating...' : 'Update Profile' }}
          </button>
        </form>
      </div>

      <!-- Change Password -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Change Password</h2>
        <form @submit.prevent="changePassword" class="space-y-4">
          <div>
            <label class="label">Current Password</label>
            <input v-model="passwordForm.currentPassword" type="password" class="input" required />
          </div>
          <div>
            <label class="label">New Password</label>
            <input v-model="passwordForm.newPassword" type="password" class="input" required />
          </div>
          <div>
            <label class="label">Confirm New Password</label>
            <input v-model="passwordForm.confirmPassword" type="password" class="input" required />
          </div>
          <button type="submit" class="btn" :disabled="loadingPassword">
            {{ loadingPassword ? 'Changing...' : 'Change Password' }}
          </button>
        </form>
      </div>

      <!-- Account Information -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Account Information</h2>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="label">User ID</span>
            <p class="text-sm text-gray-600 font-mono">{{ profile.id }}</p>
          </div>
          <div>
            <span class="label">Member Since</span>
            <p class="text-sm text-gray-600">{{ formatDate(profile.createdAt) }}</p>
          </div>
          <div>
            <span class="label">Last Login</span>
            <p class="text-sm text-gray-600">{{ formatDate(profile.lastLogin) }}</p>
          </div>
          <div>
            <span class="label">Profile Updated</span>
            <p class="text-sm text-gray-600">{{ formatDate(profile.updatedAt) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../utils/api';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  role: string;
  isActive: boolean;
  lastLogin: string | null;
  createdAt: string;
  updatedAt: string;
}

const auth = useAuthStore();
const router = useRouter();

const profile = ref<UserProfile>({
  id: '',
  username: '',
  email: '',
  firstName: '',
  lastName: '',
  role: '',
  isActive: true,
  lastLogin: null,
  createdAt: '',
  updatedAt: ''
});

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const loadingUpdate = ref(false);
const loadingPassword = ref(false);

async function loadProfile() {
  try {
    const response = await api.get('/auth/profile');
    profile.value = response.data;
  } catch (error) {
    console.error('Failed to load profile:', error);
  }
}

async function updateProfile() {
  try {
    loadingUpdate.value = true;
    await api.put('/auth/profile', {
      email: profile.value.email,
      firstName: profile.value.firstName,
      lastName: profile.value.lastName
    });
    
    // Update auth store
    await auth.fetchUser();
    alert('Profile updated successfully!');
  } catch (error: any) {
    alert(`Failed to update profile: ${error.response?.data?.message || error.message}`);
  } finally {
    loadingUpdate.value = false;
  }
}

async function changePassword() {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('New passwords do not match!');
    return;
  }

  try {
    loadingPassword.value = true;
    await api.put('/auth/change-password', {
      currentPassword: passwordForm.value.currentPassword,
      newPassword: passwordForm.value.newPassword
    });
    
    // Reset form
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    
    alert('Password changed successfully!');
  } catch (error: any) {
    alert(`Failed to change password: ${error.response?.data?.message || error.message}`);
  } finally {
    loadingPassword.value = false;
  }
}

function formatDate(dateString: string | null) {
  if (!dateString) return 'Never';
  return new Date(dateString).toLocaleString();
}

function goBack() {
  router.push('/dashboard');
}

async function onLogout() {
  await auth.logout();
  window.location.href = '/login';
}

onMounted(() => {
  loadProfile();
});
</script>

<style scoped>
.card { 
  border: 1px solid #ccc; 
  border-radius: 0.5rem; 
  padding: 1.5rem; 
  background: white;
}

.btn { 
  background-color: #374151; 
  color: white; 
  border-radius: 0.5rem; 
  padding: 0.5rem 1rem; 
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: none;
  display: inline-block;
}

.input {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem;
  font-size: 0.875rem;
  width: 100%;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input[readonly] {
  background-color: #f9fafb;
  color: #6b7280;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.badge-active {
  background-color: #10b981;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.badge-inactive {
  background-color: #6b7280;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.grid {
  display: grid;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.gap-4 {
  gap: 1rem;
}

.gap-3 {
  gap: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style>
