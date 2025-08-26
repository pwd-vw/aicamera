<template>
  <div class="p-6">
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="btn-secondary">← Back</button>
        <h1 class="text-2xl font-semibold">User Management</h1>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="auth.user">{{ auth.user.username }} ({{ auth.user.role }})</span>
        <router-link to="/profile" class="btn-secondary">Profile</router-link>
        <button class="btn" @click="onLogout">Logout</button>
      </div>
    </header>

    <div class="space-y-6">
      <!-- Create User Section -->
      <div class="card" v-if="auth.user?.role === 'admin'">
        <h2 class="text-lg font-semibold mb-4">Create New User</h2>
        <form @submit.prevent="createUser" class="grid grid-cols-2 gap-4">
          <input v-model="newUser.username" placeholder="Username" required class="input" />
          <input v-model="newUser.email" type="email" placeholder="Email" required class="input" />
          <input v-model="newUser.firstName" placeholder="First Name" class="input" />
          <input v-model="newUser.lastName" placeholder="Last Name" class="input" />
          <input v-model="newUser.password" type="password" placeholder="Password" required class="input" />
          <select v-model="newUser.role" class="input">
            <option value="viewer">Viewer</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit" class="btn col-span-2" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create User' }}
          </button>
        </form>
      </div>

      <!-- Users List -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Users</h2>
        <div v-if="loadingUsers" class="text-center py-4">Loading users...</div>
        <div v-else-if="users.length === 0" class="text-center py-4 text-gray-500">No users found</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full table-auto">
            <thead>
              <tr class="border-b">
                <th class="text-left py-2">Username</th>
                <th class="text-left py-2">Email</th>
                <th class="text-left py-2">Role</th>
                <th class="text-left py-2">Status</th>
                <th class="text-left py-2">Last Login</th>
                <th class="text-left py-2" v-if="auth.user?.role === 'admin'">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b">
                <td class="py-2">{{ user.username }}</td>
                <td class="py-2">{{ user.email }}</td>
                <td class="py-2">
                  <span :class="user.role === 'admin' ? 'badge-admin' : 'badge-viewer'">
                    {{ user.role }}
                  </span>
                </td>
                <td class="py-2">
                  <span :class="user.isActive ? 'badge-active' : 'badge-inactive'">
                    {{ user.isActive ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="py-2">{{ formatDate(user.lastLogin) }}</td>
                <td class="py-2" v-if="auth.user?.role === 'admin'">
                  <button @click="toggleUserStatus(user)" class="btn-sm btn-secondary mr-2">
                    {{ user.isActive ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button @click="deleteUser(user)" class="btn-sm btn-danger" v-if="user.id !== auth.user?.id">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
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

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  isActive: boolean;
  lastLogin: string | null;
  firstName?: string;
  lastName?: string;
}

const auth = useAuthStore();
const router = useRouter();

const users = ref<User[]>([]);
const loadingUsers = ref(false);
const loading = ref(false);
const newUser = ref({
  username: '',
  email: '',
  firstName: '',
  lastName: '',
  password: '',
  role: 'viewer'
});

async function loadUsers() {
  try {
    loadingUsers.value = true;
    const response = await api.get('/users');
    users.value = response.data;
  } catch (error) {
    console.error('Failed to load users:', error);
  } finally {
    loadingUsers.value = false;
  }
}

async function createUser() {
  try {
    loading.value = true;
    const endpoint = newUser.value.role === 'admin' ? '/auth/create-admin' : '/auth/register';
    await api.post(endpoint, newUser.value);
    
    // Reset form
    newUser.value = {
      username: '',
      email: '',
      firstName: '',
      lastName: '',
      password: '',
      role: 'viewer'
    };
    
    // Reload users
    await loadUsers();
    alert('User created successfully!');
  } catch (error: any) {
    alert(`Failed to create user: ${error.response?.data?.message || error.message}`);
  } finally {
    loading.value = false;
  }
}

async function toggleUserStatus(user: User) {
  try {
    await api.put(`/users/${user.id}/status`, { isActive: !user.isActive });
    user.isActive = !user.isActive;
  } catch (error: any) {
    alert(`Failed to update user status: ${error.response?.data?.message || error.message}`);
  }
}

async function deleteUser(user: User) {
  if (!confirm(`Are you sure you want to delete user "${user.username}"?`)) {
    return;
  }
  
  try {
    await api.delete(`/users/${user.id}`);
    users.value = users.value.filter(u => u.id !== user.id);
    alert('User deleted successfully!');
  } catch (error: any) {
    alert(`Failed to delete user: ${error.response?.data?.message || error.message}`);
  }
}

function formatDate(dateString: string | null) {
  if (!dateString) return 'Never';
  return new Date(dateString).toLocaleDateString();
}

function goBack() {
  router.push('/dashboard');
}

async function onLogout() {
  await auth.logout();
  window.location.href = '/login';
}

onMounted(() => {
  loadUsers();
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

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-danger {
  background-color: #dc2626;
  color: white;
}

.input {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem;
  font-size: 0.875rem;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.badge-admin {
  background-color: #dc2626;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.badge-viewer {
  background-color: #059669;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
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

.col-span-2 {
  grid-column: span 2;
}

.gap-4 {
  gap: 1rem;
}

.gap-3 {
  gap: 0.75rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.overflow-x-auto {
  overflow-x: auto;
}
</style>
