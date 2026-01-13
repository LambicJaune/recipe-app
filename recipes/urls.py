from django.urls import path
from .views import AboutView, UserProfileView, recipes_home, RecipeListView, RecipeDetailView, ChartView, RecipeCreateView, RecipeSearchView

app_name = 'recipes'

urlpatterns = [
    path('', recipes_home, name='recipes_home'),
    path('overview/', RecipeListView.as_view(), name='recipes_overview'),
    path('overview/<pk>/', RecipeDetailView.as_view(), name='recipe_detail'),
    path('charts/', ChartView.as_view(), name='recipe_charts'),
    path('create/', RecipeCreateView.as_view(), name='recipe_create'),
    path('search/', RecipeSearchView.as_view(), name='recipe_search'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('about/', AboutView.as_view(), name='about_the_dev'),
]