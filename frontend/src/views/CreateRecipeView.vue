<template>
  <div class="create-recipe container mt-4">
    <h1>创建新菜谱</h1>
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
        <label for="image" class="form-label">图片</label>
        <input type="file" class="form-control" id="image" @change="handleFileChange">
      </div>
      <button type="submit" class="btn btn-primary">创建</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();

const recipe = ref({
  title: '',
  description: '',
  tags: '' // Add tags property
});

const selectedFile = ref(null);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

const handleSubmit = async () => {
  try {
    let imageUrl = null;
    // 1. Upload image if selected
    if (selectedFile.value) {
      const uploadResponse = await api.uploadImage(selectedFile.value);
      imageUrl = uploadResponse.data.image_url;
    }

    // 2. Create recipe with image URL and tags
    const recipeData = {
      ...recipe.value,
      image_url: imageUrl,
    };

    await api.createRecipe(recipeData);

    // 3. Redirect to home page
    router.push('/');

  } catch (error) {
    console.error('Failed to create recipe:', error);
    alert('创建失败，请查看控制台获取更多信息。');
  }
};
</script>

<style scoped>
.create-recipe {
  max-width: 600px;
  margin: auto;
}
</style>