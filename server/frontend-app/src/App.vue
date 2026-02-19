<template>
  <div id="app">
    <nav class="nav">
      <router-link to="/">Server (Detection)</router-link>
      <router-link to="/network">Network</router-link>
      <router-link to="/edge_control">Edge Control</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 0 1rem 2rem;
}
.nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}
.nav a {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 500;
}
.nav a:hover { text-decoration: underline; }
.nav a.router-link-active { color: #0a58ca; font-weight: 600; }
main { min-height: 40vh; }
</style>
