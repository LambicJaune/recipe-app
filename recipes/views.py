from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

import pandas as pd

from .models import Recipe
from .forms import RecipeSearchForm, RecipeCreateForm, CustomUserChangeForm
from .utils import get_chart

# Home page
def recipes_home(request):
    """
    Render the home page of the recipes application.
    """
    return render(request, 'recipes/recipes_home.html')


# -------------------------
# OVERVIEW OF ALL RECIPES
# -------------------------

class RecipeListView(LoginRequiredMixin, ListView):
    """
    Display a paginated list of recipes with search and filter capabilities.

    Supports filtering by recipe name, ingredients, difficulty level, and maximum cooking time.
    Renders both a table view (using Pandas DataFrame) and a card layout for each recipe.
    """
    model = Recipe
    template_name = 'recipes/recipes_overview.html'
    context_object_name = 'recipes'
    paginate_by = 16

    def get_queryset(self):
        """
        Retrieve and filter the queryset of recipes based on search criteria provided via GET parameters.
        """
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
        """
        Add search form and formatted DataFrame to the context for rendering.
        Also prepares ingredient lists for card layout.
        """
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
                    f'<img src="{obj.pic_or_default}" width="80" />'
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
        """
        Extract and return a sorted list of unique ingredients from all recipes for use in search forms.
        """
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


# -------------------------
# CHARTS VIEW
# -------------------------

class ChartView(LoginRequiredMixin, TemplateView):
    """
    Display various charts summarizing recipe data using Matplotlib based on cooking time and difficulty.
    """
    template_name = "recipes/recipe_charts.html"

    def get_context_data(self, **kwargs):
        """
        Build chart data using Pandas and pass rendered charts to the template context.
        """
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

# -------------------------
# CREATE RECIPE FORM VIEW
# -------------------------

class RecipeCreateView(CreateView):
    """
    Provide a form for users to create and add new recipes to the database.
    """
    model = Recipe
    form_class = RecipeCreateForm
    template_name = 'recipes/recipe_create.html'

    def get_success_url(self):
        """
        Redirect to the recipes overview page upon successful recipe creation.
        """
        return reverse_lazy('recipes:recipes_overview')
    
# -------------------------
# RECIPE SEARCH VIEW
# -------------------------

class RecipeSearchView(LoginRequiredMixin, ListView):
    """
    Display a paginated list of recipes based on search criteria.

    Supports filtering by recipe name, ingredients, difficulty level, and maximum cooking time.
    Renders results in a table format using Pandas DataFrame.
    """
    model = Recipe
    template_name = 'recipes/recipe_search.html'
    context_object_name = 'recipes'
    paginate_by = 16

    def get_queryset(self):
        """
        Retrieve and filter the queryset of recipes based on search criteria.
        """
        qs = Recipe.objects.all().order_by('name')

        # Ingredient choices
        ingredient_choices = self.get_ingredient_choices()

        # Bound form
        self.form = RecipeSearchForm(self.request.GET or None, ingredient_choices=ingredient_choices)

        if self.request.GET and self.form.is_valid():
            name = self.form.cleaned_data.get('recipe_name')
            ingredients = self.form.cleaned_data.get('ingredient')
            difficulty = self.form.cleaned_data.get('difficulty_level')
            max_time = self.form.cleaned_data.get('max_cooking_time')

            if name:
                qs = qs.filter(name__icontains=name)

            if ingredients:
                ingredient_q = Q()
                for ing in ingredients:
                    ingredient_q |= Q(ingredients__icontains=ing)
                qs = qs.filter(ingredient_q)

            if difficulty:
                qs = qs.filter(pk__in=[r.pk for r in qs if r.calculate_difficulty.lower() == difficulty.lower()])

            if max_time is not None:
                qs = qs.filter(cooking_time__lte=max_time)

        return qs

    def get_context_data(self, **kwargs):
        """
        Add search form and formatted DataFrame to the context for rendering.
        """
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form

        # Build DataFrame for table
        data = []
        for obj in context['recipes']:
            recipe_url = reverse("recipes:recipe_detail", args=[obj.pk])
            data.append({
                "Name": f'<a href="{recipe_url}">{obj.name}</a>',
                "Difficulty": obj.calculate_difficulty,
                "Cooking Time (min)": obj.cooking_time,
                "Ingredients": obj.ingredients,
                "Picture": f'<img src="{obj.pic_or_default}" width="80" />'
            })
        df = pd.DataFrame(data)
        context['df_html'] = df.to_html(classes='table table-striped', index=False, escape=False)

        return context

    def get_ingredient_choices(self):
        """
        Extract and return a sorted list of unique ingredients from all recipes for search filtering.
        """
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


# -------------------------
# SINGLE RECIPE VIEW
# -------------------------

class RecipeDetailView(LoginRequiredMixin, DetailView):
    """
    Display detailed information about a single recipe.
    """
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

# -------------------------
# USER PROFILE VIEW
# -------------------------

User = get_user_model()


class UserProfileView(LoginRequiredMixin, TemplateView):
    """
    Allow users to view and update their profile information and change their password.
    """
    template_name = "recipes/user.html"

    def get_context_data(self, **kwargs):
        """
        Add profile update and password change forms to the context.
        """
        context = super().get_context_data(**kwargs)
        context["profile_form"] = CustomUserChangeForm(instance=self.request.user)
        context["password_form"] = PasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle profile updates and password changes based on submitted forms.
        """

        # PROFILE UPDATE FORM
        if "update_profile" in request.POST:
            profile_form = CustomUserChangeForm(
                request.POST, instance=request.user
            )
            password_form = PasswordChangeForm(user=request.user)

            if profile_form.is_valid():
                profile_form.save()

        # PASSWORD CHANGE FORM
        elif "change_password" in request.POST:
            profile_form = CustomUserChangeForm(instance=request.user)
            password_form = PasswordChangeForm(
                user=request.user,
                data=request.POST
            )

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # IMPORTANT
                return redirect("recipes:user_profile")

        return self.render_to_response({
            "profile_form": profile_form,
            "password_form": password_form,
        })

# -------------------------
# ABOUT THE DEV VIEW
# -------------------------

class AboutView(LoginRequiredMixin, TemplateView):
    """
    Display information about the developer.
    """
    template_name = "recipes/about_the_dev.html"

    def get_context_data(self, **kwargs):
        """
        Add developer information (metadata) to the context for rendering.
        """
        context = super().get_context_data(**kwargs)

        context["developer"] = {
                "name": "GAEL GIRAUD",
                "title": "Full-Stack Developer (Python / Django / JavaScript)",
                "intro": (
                    "I'm a full-stack developer with a strong backend focus on Python and Django. "
                    "I build clean, maintainable applications and enjoy working across the stack, "
                    "from backend APIs to modern frontend interfaces."
                ),

                "skills": {
                    "Backend": [
                        "Python",
                        "Django (CBVs, ORM, Auth, Forms)",
                        "RESTful API design",
                        "Data processing with Pandas",
                    ],
                    "Frontend": [
                        "React (JWT auth, protected routes, caching)",
                        "Angular (TypeScript, RxJS, Material, accessibility)",
                        "Responsive design & UI state management",
                        "Data visualization (Recharts)",
                    ],
                    "APIs & Cloud": [
                        "Node.js & Express",
                        "MongoDB Atlas (Mongoose)",
                        "Authentication (JWT, Passport.js)",
                        "AWS Lambda (serverless)",
                        "Deployment (Heroku)",
                    ],
                    "Mobile": [
                        "React Native / Expo with Firebase (auth & real-time data)",
                    ],
                },

                "soft_skills": [
                    "Clear communication with non-technical stakeholders",
                    "Experience working with developers and support teams",
                    "Highly adaptable, self-taught career transition",
                    "Strong focus on quality, maintainability, and documentation",
                ],

                "links": {
                    "github": "https://github.com/lambicjaune",
                    "portfolio": "https://lambicjaune.github.io/portfolio-website/",
                },

                "image": "recipes/images/developer.jpg",
            }

        return context