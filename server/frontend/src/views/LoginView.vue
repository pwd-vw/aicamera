<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <form class="w-full max-w-sm space-y-4" @submit.prevent="onSubmit">
      <h1 class="text-2xl font-semibold">Sign in</h1>
      <div>
        <label class="block text-sm mb-1">Username</label>
        <input v-model="username" class="input" type="text" required />
      </div>
      <div>
        <label class="block text-sm mb-1">Password</label>
        <input v-model="password" class="input" type="password" required />
      </div>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <button class="btn" :disabled="loading">{{ loading ? 'Signing in...' : 'Sign in' }}</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref('');
const password = ref('');

const loading = computed(() => auth.loading);
const error = computed(() => auth.error);

async function onSubmit() {
  const ok = await auth.login(username.value, password.value);
  if (ok) {
    const redirect = (route.query.redirect as string) || '/';
    router.replace(redirect);
  }
}
</script>

<style scoped>
.input { 
  width: 100%; 
  border: 1px solid #ccc; 
  border-radius: 0.5rem; 
  padding: 0.5rem 0.75rem; 
}
.btn { 
  width: 100%; 
  background-color: #2563eb; 
  color: white; 
  border-radius: 0.5rem; 
  padding: 0.5rem 0.75rem; 
  border: none;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
