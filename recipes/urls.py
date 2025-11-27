from django.urls import path
from .views import recipes_home, RecipeListView, RecipeDetailView

app_name = 'recipes'

urlpatterns = [
    path('', recipes_home, name='recipes_home'),
    path('overview/', RecipeListView.as_view(), name='recipes_overview'),
    path('overview/<pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
]