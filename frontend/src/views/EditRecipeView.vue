<template>
  <div class="edit-recipe container mt-4">
    <h1>编辑菜谱</h1>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="title" class="form-label">标题</label>
        <input type="text" class="form-control" id="title" v-model="recipe.title" required>
      </div>
      <div class="mb-3">
        <label for="description" class="form-label">描述</label>
        <textarea class="form-control" id="description" rows="3" v-model="recipe.description" required></textarea>
      </div>
      <div class="mb-3">
        <label for="tags" class="form-label">标签 (用逗号分隔)</label>
        <input type="text" class="form-control" id="tags" v-model="recipe.tags">
      </div>
      <div class="mb-3">
        <label for="image" class="form-label">新图片 (可选)</label>
        <input type="file" class="form-control" id="image" @change="handleFileChange">
        <p v-if="recipe.image_url">当前图片: <a :href="recipe.image_url" target="_blank">查看</a></p>
      </div>
      <button type="submit" class="btn btn-primary">保存更改</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();
const recipeId = route.params.id;

// Use a ref for the editable tags string
const recipe = ref({ title: '', description: '', image_url: null, tags: '' });
const selectedFile = ref(null);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

const handleSubmit = async () => {
  try {
    let imageUrl = recipe.value.image_url;
    // 1. Upload new image if selected
    if (selectedFile.value) {
      const uploadResponse = await api.uploadImage(selectedFile.value);
      imageUrl = uploadResponse.data.image_url;
    }

    // 2. Update recipe with new data
    const recipeData = {
      title: recipe.value.title,
      description: recipe.value.description,
      image_url: imageUrl,
      tags: recipe.value.tags // Send the comma-separated string
    };

    await api.updateRecipe(recipeId, recipeData);

    // 3. Redirect to home page
    router.push('/');

  } catch (error) {
    console.error('Failed to update recipe:', error);
    alert('更新失败，请查看控制台获取更多信息。');
  }
};

onMounted(async () => {
  try {
    const response = await api.getRecipe(recipeId);
    const fetchedRecipe = response.data;
    
    // Format tags array into a comma-separated string for the input
    fetchedRecipe.tags = fetchedRecipe.tags.map(tag => tag.name).join(', ');
    
    recipe.value = fetchedRecipe;

  } catch (error) {
    console.error('Failed to fetch recipe details:', error);
  }
});
</script>

<style scoped>
.edit-recipe {
  max-width: 600px;
  margin: auto;
}
</style>
