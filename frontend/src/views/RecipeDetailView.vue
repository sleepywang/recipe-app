<template>
  <div class="container mt-4" v-if="recipe">
    <h1>{{ recipe.title }}</h1>
    <img :src="recipe.image_url" class="img-fluid mb-3" alt="Recipe image" v-if="recipe.image_url">
    <p class="lead">{{ recipe.description }}</p>
    <div>
      <h4>Tags</h4>
      <span v-for="tag in recipe.tags" :key="tag.id" class="badge bg-secondary me-1">{{ tag.name }}</span>
    </div>
    <hr>
    <RouterLink to="/" class="btn btn-primary">返回菜谱列表</RouterLink>
  </div>
  <div v-else class="container mt-4">
    <p>正在加载...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';

const recipe = ref(null);
const route = useRoute();

const fetchRecipe = async () => {
  try {
    const response = await api.getRecipe(route.params.id);
    recipe.value = response.data;
  } catch (error) {
    console.error('Failed to fetch recipe:', error);
  }
};

onMounted(() => {
  fetchRecipe();
});
</script>

<style scoped>
.img-fluid {
  max-height: 400px;
  object-fit: cover;
}
</style>
