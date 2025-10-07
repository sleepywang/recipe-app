<template>
  <div class="container mt-4">
    <div class="row">
      <!-- Left column for tags -->
      <div class="col-md-3">
        <h4>Tags</h4>
        <ul class="list-group">
          <li class="list-group-item list-group-item-action" @click="selectTag(null)" :class="{ 'active': selectedTag === null }">
            All Recipes
          </li>
          <li v-for="tag in tags" :key="tag.id" class="list-group-item list-group-item-action" @click="selectTag(tag)" :class="{ 'active': selectedTag && selectedTag.id === tag.id }">
            {{ tag.name }}
          </li>
        </ul>
      </div>

      <!-- Right column for recipes -->
      <div class="col-md-9">
        <h1 v-if="selectedTag">{{ selectedTag.name }}</h1>
        <h1 v-else>All Recipes</h1>
        <hr>
        <div class="list-group">
          <div v-if="filteredRecipes.length > 0">
            <div v-for="recipe in filteredRecipes" :key="recipe.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
              <RouterLink :to="`/recipes/${recipe.id}`" class="text-decoration-none text-dark d-flex align-items-center">
                <img :src="recipe.image_url" class="thumbnail me-3" alt="Recipe thumbnail" v-if="recipe.image_url">
                <h5 class="mb-0">{{ recipe.title }}</h5>
              </RouterLink>
              <div>
                <RouterLink :to="`/edit/${recipe.id}`" class="btn btn-sm btn-outline-secondary me-2" title="修改">
                  <i class="bi bi-pencil"></i>
                </RouterLink>
                <button @click="deleteRecipe(recipe.id)" class="btn btn-sm btn-outline-danger" title="删除">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="alert alert-info">
            No recipes found for this tag.
          </div>
        </div>
        <RouterLink to="/create" class="btn btn-success mt-3">创建新菜谱</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { RouterLink } from 'vue-router';
import api from '../services/api';

const recipes = ref([]);
const tags = ref([]);
const selectedTag = ref(null);

const fetchRecipes = async () => {
  try {
    const response = await api.getRecipes();
    recipes.value = response.data;
  } catch (error) {
    console.error('Failed to fetch recipes:', error);
  }
};

const fetchTags = async () => {
  try {
    const response = await api.getTags();
    tags.value = response.data;
  } catch (error) {
    console.error('Failed to fetch tags:', error);
  }
};

const deleteRecipe = async (id) => {
  if (confirm('您确定要删除这个菜谱吗？')) {
    try {
      await api.deleteRecipe(id);
      fetchRecipes();
    } catch (error) {
      console.error('Failed to delete recipe:', error);
      alert('删除失败！');
    }
  }
};

const selectTag = (tag) => {
  selectedTag.value = tag;
};

const filteredRecipes = computed(() => {
  if (!selectedTag.value) {
    return recipes.value;
  }
  return recipes.value.filter(recipe =>
    recipe.tags.some(tag => tag.id === selectedTag.value.id)
  );
});

onMounted(() => {
  fetchRecipes();
  fetchTags();
});
</script>

<style scoped>
.thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 5px;
}
.list-group-item-action {
  cursor: pointer;
}
</style>
