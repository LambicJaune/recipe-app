from django.shortcuts import render
from django.views.generic import ListView, DetailView   
from .models import Recipe

# Create your views here.

def recipes_home(request):
   return render(request, 'recipes/recipes_home.html')

class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipes_overview.html'
    context_object_name = 'recipes'

class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'