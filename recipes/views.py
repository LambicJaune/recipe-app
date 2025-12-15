from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

import pandas as pd

from .models import Recipe
from .forms import RecipeSearchForm, RecipeCreateForm
from .utils import get_chart


# Home page
def recipes_home(request):
    return render(request, 'recipes/recipes_home.html')


class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/recipes_overview.html'
    context_object_name = 'recipes'
    paginate_by = 16

    def get_queryset(self):
        qs = Recipe.objects.all().order_by('name')

        # Build ingredient choices first
        ingredient_choices = self.get_ingredient_choices()

        # Initialize form (bound only if GET data exists)
        self.form = RecipeSearchForm(
            data=self.request.GET or None,
            ingredient_choices=ingredient_choices
        )

        if self.request.GET and self.form.is_valid():
            recipe_name = self.form.cleaned_data.get("recipe_name")
            ingredients = self.form.cleaned_data.get("ingredient")
            difficulty = self.form.cleaned_data.get("difficulty_level")
            max_time = self.form.cleaned_data.get("max_cooking_time")

            if recipe_name:
                qs = qs.filter(name__icontains=recipe_name)

            if ingredients:
                ingredient_q = Q()
                for ing in ingredients:
                    ingredient_q |= Q(ingredients__icontains=ing)
                qs = qs.filter(ingredient_q)

            if difficulty:
                qs = qs.filter(
                    pk__in=[
                        r.pk for r in qs
                        if r.calculate_difficulty.lower() == difficulty.lower()
                    ]
                )

            if max_time is not None:
                qs = qs.filter(cooking_time__lte=max_time)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form

        qs = context["recipes"]

        # Build DataFrame for table view
        data = []
        for obj in qs:
            recipe_url = reverse("recipes:recipe_detail", args=[obj.pk])

            data.append({
                "Name": f'<a href="{recipe_url}">{obj.name}</a>',
                "Difficulty": obj.calculate_difficulty,
                "Cooking Time (min)": obj.cooking_time,
                "Ingredients": obj.ingredients,
                "Picture": (
                    f'<img src="{obj.pic.url}" width="80" />'
                    if obj.pic else ""
                )
            })

        df = pd.DataFrame(data)

        context['df_html'] = df.to_html(
            classes='table table-striped',
            index=False,
            escape=False
        )

        # Ingredient list for card layout
        for recipe in context['recipes']:
            recipe.ingredient_list = [
                i.strip()
                for i in recipe.ingredients.replace("\n", ",").split(",")
                if i.strip()
            ]

        return context

    def get_ingredient_choices(self):
        all_ingredients = Recipe.objects.values_list('ingredients', flat=True)
        ingredient_set = set()

        for ingredient_block in all_ingredients:
            if ingredient_block:
                raw_ingredients = ingredient_block.replace("\n", ",").split(",")
                for ing in raw_ingredients:
                    clean = ing.strip()
                    if clean:
                        ingredient_set.add(clean)

        return [(ing, ing) for ing in sorted(ingredient_set)]


class ChartView(LoginRequiredMixin, TemplateView):
    template_name = "recipes/recipe_charts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipes = Recipe.objects.all()
        data = [{
            "name": r.name,
            "cooking_time": r.cooking_time,
            "difficulty": r.calculate_difficulty
        } for r in recipes]

        df = pd.DataFrame(data)

        if not df.empty:
            bar_data = (
                df.groupby("difficulty")["cooking_time"]
                .mean()
                .reset_index()
                .rename(columns={"cooking_time": "AvgCookingTime"})
            )

            context['charts'] = {
                "bar": get_chart("bar", data=bar_data),
                "pie": get_chart(
                    "pie",
                    labels=df["difficulty"].value_counts().index.tolist(),
                    sizes=df["difficulty"].value_counts().tolist(),
                ),
                "line": get_chart(
                    "line",
                    data=df.sort_values("cooking_time")
                        .assign(CumulativeCount=lambda x: range(1, len(x) + 1))
                ),
            }
        else:
            context['charts'] = {"bar": None, "pie": None, "line": None}

        return context


class RecipeCreateView(CreateView):
    model = Recipe
    form_class = RecipeCreateForm
    template_name = 'recipes/recipe_create.html'

    def get_success_url(self):
        return reverse_lazy('recipes:recipes_overview')


class RecipeDetailView(LoginRequiredMixin, DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'
