<template>
  <div class="create-recipe container mt-4">
    <h1>创建新菜谱</h1>
    <div class="row">
      <!-- Left column for the form -->
      <div class="col-md-7">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="title" class="form-label">标题</label>
            <div class="input-group">
              <input type="text" class="form-control" id="title" v-model="recipe.title" required>
              <button class="btn btn-outline-primary" type="button" @click="getAiSuggestions" :disabled="isSuggesting">
                <span v-if="isSuggesting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ isSuggesting ? 'Suggesting...' : 'AI 建议' }}
              </button>
            </div>
          </div>
          <div class="mb-3">
            <label for="description" class="form-label">描述</label>
            <textarea class="form-control" id="description" rows="10" v-model="recipe.description" required></textarea>
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

      <!-- Right column for AI suggestions -->
      <div class="col-md-5">
        <h4>AI 建议</h4>
        <div v-if="isSuggesting" class="d-flex justify-content-center mt-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="suggestions" class="card">
          <div class="card-body">
            <h5 class="card-title">建议的步骤</h5>
            <p class="card-text" style="white-space: pre-wrap;">{{ suggestions.description }}</p>
            <button class="btn btn-success" @click="acceptSuggestions">采纳建议</button>
          </div>
        </div>
        <div v-else class="text-muted">
          点击 "AI 建议" 按钮来获取步骤的灵感。
        </div>
      </div>
    </div>
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
  tags: '',
});

const selectedFile = ref(null);
const suggestions = ref(null);
const isSuggesting = ref(false);

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};

const getAiSuggestions = async () => {
  if (!recipe.value.title) {
    alert('请输入菜谱标题以获取建议。');
    return;
  }
  isSuggesting.value = true;
  suggestions.value = null;

  try {
    const response = await api.getAiSuggestions(recipe.value.title);
    suggestions.value = response.data;
  } catch (error) {
    console.error('Failed to get AI suggestions:', error);
    alert('获取AI建议失败。');
  } finally {
    isSuggesting.value = false;
  }
};

const acceptSuggestions = () => {
  if (suggestions.value) {
    recipe.value.description = suggestions.value.description;
  }
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
  max-width: 100%;
}
</style>