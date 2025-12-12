from multiprocessing import context
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView   
from .models import Recipe
# to protect class-based view
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeSearchForm
from django.db.models import Q
import pandas as pd
from django.views.generic import TemplateView
from .utils import get_chart

# Create your views here.

def recipes_home(request):
   return render(request, 'recipes/recipes_home.html')

class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/recipes_overview.html'
    context_object_name = 'recipes'
    paginate_by = 16

    def get_queryset(self):
        qs = Recipe.objects.all().order_by('name')

        # Get all ingredient choices first
        ingredient_choices = self.get_ingredient_choices()

        # Initialize form with choices before binding GET data
        self.form = RecipeSearchForm(
            data=self.request.GET or None,
            ingredient_choices=ingredient_choices
        )


        if self.form.is_valid():
            recipe_name = self.form.cleaned_data.get("recipe_name")
            ingredients = self.form.cleaned_data.get("ingredient")
            difficulty = self.form.cleaned_data.get("difficulty_level")
            max_time = self.form.cleaned_data.get("max_cooking_time")

            print("\n--- DEBUG SEARCH FILTERS ---")
            print("Initial queryset:", qs)

            if recipe_name:
                qs = qs.filter(name__icontains=recipe_name)
                print(f"After filtering by recipe_name='{recipe_name}':", qs)

             # Filter by ingredients
            if ingredients:
                ingredient_q = Q()
                for ing in ingredients:
                    ingredient_q |= Q(ingredients__icontains=ing)
                qs = qs.filter(ingredient_q)
                print(f"After filtering by ingredients {ingredients}:", qs)

            # Filter by difficulty
            if difficulty:
                qs = qs.filter(pk__in=[
                    r.pk for r in qs if r.calculate_difficulty.lower() == difficulty.lower()
                ])
                print(f"After filtering by difficulty='{difficulty}':", qs)

            if max_time is not None:
                qs = qs.filter(cooking_time__lte=max_time)
                print(f"After filtering by max_cooking_time<={max_time}:", qs)

            print("Final filtered queryset:", qs)
            print("Count:", qs.count())
            print("--- END DEBUG ---\n")
        else:
            print("\nForm is not valid or no GET data provided.")
            print("Errors:", self.form.errors)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form

        # Build DataFrame from full filtered queryset
        qs = context["recipes"]

        data = []
        for obj in qs:
            # Create link for recipe name
            recipe_url = reverse("recipes:recipe_detail", args=[obj.pk])
            name_link = f'<a href="{recipe_url}">{obj.name}</a>'

            data.append({
                "Name": name_link,
                "Difficulty": obj.calculate_difficulty,
                "Cooking Time (min)": obj.cooking_time,
                "Ingredients": obj.ingredients,
                "Picture": (
                    f'<img src="{obj.pic.url}" width="80" />'
                    if obj.pic else ""
                )
            })

        df = pd.DataFrame(data)

        # Convert to HTML table (with images allowed)
        context['df_html'] = df.to_html(
            classes='table table-striped',
            index=False,
            escape=False  # <-- required to render <img> tags
        )

        # Existing ingredient list for card layout (unchanged)
        for recipe in context['recipes']:
            recipe.ingredient_list = [
                i.strip() for i in recipe.ingredients.splitlines() if i.strip()
            ]

        return context


    def get_ingredient_choices(self):
        all_ingredients = Recipe.objects.values_list('ingredients', flat=True)
        ingredient_set = set()

        for ingredient_block in all_ingredients:
            if ingredient_block:
                # split by comma AND newline
                raw_ingredients = ingredient_block.replace("\n", ",").split(",")

                for ing in raw_ingredients:
                    clean = ing.strip()
                    if clean:
                        ingredient_set.add(clean)

        # return sorted list of individual ingredients
        return [(ing, ing) for ing in sorted(ingredient_set)]
    
class ChartView(LoginRequiredMixin, TemplateView):
    template_name = "recipes/recipe_charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Query all recipes
        recipes = Recipe.objects.all()
        data = [{
            "name": r.name,
            "cooking_time": r.cooking_time,
            "difficulty": r.calculate_difficulty
        } for r in recipes]

        df = pd.DataFrame(data)

        if not df.empty:
            # Bar chart: avg cooking time by difficulty
            bar_data = df.groupby("difficulty")["cooking_time"].mean().reset_index()
            bar_data.rename(columns={"cooking_time": "AvgCookingTime"}, inplace=True)
            bar_chart = get_chart("bar", data=bar_data)

            # Pie chart: count per difficulty
            pie_labels = df["difficulty"].value_counts().index.tolist()
            pie_sizes = df["difficulty"].value_counts().tolist()
            pie_chart = get_chart("pie", labels=pie_labels, sizes=pie_sizes)

            # Line chart: cumulative by cooking time
            df_sorted = df.sort_values("cooking_time")
            df_sorted["CumulativeCount"] = range(1, len(df_sorted) + 1)
            line_chart = get_chart("line", data=df_sorted)

            context['charts'] = {
                "bar": bar_chart,
                "pie": pie_chart,
                "line": line_chart,
            }
        else:
            context['charts'] = {"bar": None, "pie": None, "line": None}

        return context

class RecipeDetailView(LoginRequiredMixin, DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'
