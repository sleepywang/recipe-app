import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CreateRecipeView from '../views/CreateRecipeView.vue'
import EditRecipeView from '../views/EditRecipeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/create',
      name: 'create',
      component: CreateRecipeView
    },
    {
      path: '/edit/:id',
      name: 'edit',
      component: EditRecipeView
    },
    {
      path: '/recipes/:id',
      name: 'recipe-detail',
      component: () => import('../views/RecipeDetailView.vue')
    }
  ]
})

export default router
