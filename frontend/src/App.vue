<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container">
        <RouterLink class="navbar-brand" to="/">菜谱网站</RouterLink>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/">主页</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/create">创建菜谱</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <main class="container mt-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<style>
/* You can add global styles here if needed */
</style>
