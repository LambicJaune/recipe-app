from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Recipe
from .views import recipes_home, RecipeListView, RecipeDetailView, ChartView
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

# ---------------------------------------------
# Helper functions
# ---------------------------------------------
def create_recipe(name="Test Recipe", cooking_time=20, ingredients="Eggs\nMilk", pic=None):
    if pic is None:
        pic = get_dummy_image()
    return Recipe.objects.create(
        name=name,
        cooking_time=cooking_time,
        ingredients=ingredients,
        pic=pic
    )

def get_dummy_image():
    """Returns a simple in-memory PNG image for testing."""
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), "white")
    image.save(file, "PNG")
    file.seek(0)
    return SimpleUploadedFile("test.png", file.read(), content_type="image/png")

# ---------------------------------------------
# HOME VIEW TESTS
# ---------------------------------------------
class HomeViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        url = reverse("recipes:recipes_home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipes_home.html")


# ---------------------------------------------
# LOGIN REQUIRED TESTS
# ---------------------------------------------
class LoginRequiredTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test", password="pass123")

    def test_overview_requires_login(self):
        url = reverse("recipes:recipes_overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  
        self.assertIn("/login", response.url)

    def test_chart_view_requires_login(self):
        url = reverse("recipes:recipe_charts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_detail_requires_login(self):
        recipe = create_recipe()
        url = reverse("recipes:recipe_detail", args=[recipe.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)


# ---------------------------------------------
# RECIPE OVERVIEW (LIST VIEW)
# ---------------------------------------------
class RecipeListViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="pass123")
        self.client.login(username="tester", password="pass123")

        # Create recipes
        create_recipe("Pancakes", 10, "Eggs\nFlour\nMilk")
        create_recipe("Spaghetti", 30, "Tomatoes\nPasta")
        create_recipe("Omelette", 5, "Eggs\nSalt")

    def test_overview_page_loads(self):
        url = reverse("recipes:recipes_overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipes_overview.html")
        self.assertIn("df_html", response.context)

    def test_search_filter_by_name(self):
        url = reverse("recipes:recipes_overview")
        response = self.client.get(url, {"recipe_name": "panc"})
        self.assertContains(response, "Pancakes")
        self.assertNotContains(response, "Spaghetti")

    def test_search_filter_by_ingredient(self):
        url = reverse("recipes:recipes_overview")
        response = self.client.get(url, {"ingredient": "Eggs"})
        self.assertContains(response, "Pancakes")
        self.assertContains(response, "Omelette")
        self.assertNotContains(response, "Spaghetti")

    def test_search_invalid_form(self):
        url = reverse("recipes:recipes_overview")
        response = self.client.get(url, {"max_cooking_time": "not-a-number"})
        # Should not crash — form should be invalid and return all recipes
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pancakes")
        self.assertContains(response, "Spaghetti")
        self.assertContains(response, "Omelette")

    def test_pagination(self):
        for i in range(20):
            create_recipe(f"R{i}", 5)

        url = reverse("recipes:recipes_overview")
        response = self.client.get(url)
        self.assertEqual(len(response.context["recipes"]), 16)


# ---------------------------------------------
# DETAIL VIEW
# ---------------------------------------------
class RecipeDetailViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass123")
        self.client.login(username="tester", password="pass123")
        self.recipe = create_recipe()

    def test_detail_page_loads(self):
        url = reverse("recipes:recipe_detail", args=[self.recipe.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertEqual(response.context["recipe"].pk, self.recipe.pk)


# ---------------------------------------------
# CHART VIEW TESTS
# ---------------------------------------------
class ChartViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass123")
        self.client.login(username="tester", password="pass123")

        create_recipe("R1", 5)
        create_recipe("R2", 10)

    def test_chart_page_loads(self):
        url = reverse("recipes:recipe_charts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_charts.html")

    def test_charts_exist_in_context(self):
        url = reverse("recipes:recipe_charts")
        response = self.client.get(url)
        charts = response.context["charts"]
        self.assertIn("bar", charts)
        self.assertIn("pie", charts)
        self.assertIn("line", charts)
        self.assertIsNotNone(charts["bar"])

    def test_back_button_present(self):
        url = reverse("recipes:recipe_charts")
        response = self.client.get(url)
        self.assertContains(response, reverse("recipes:recipes_overview"))


# ---------------------------------------------
# FORM TESTS
# ---------------------------------------------
from .forms import RecipeSearchForm

class RecipeSearchFormTests(TestCase):

    def test_valid_form(self):
        form = RecipeSearchForm(data={
            "recipe_name": "cake",
            "ingredient": ["Sugar"],
            "difficulty_level": "easy",
            "max_cooking_time": 30
        }, ingredient_choices=[("Sugar","Sugar")])
        self.assertTrue(form.is_valid())

    def test_invalid_max_time(self):
        form = RecipeSearchForm(data={
            "max_cooking_time": "wrong"
        }, ingredient_choices=[])
        self.assertFalse(form.is_valid())

    def test_empty_form_is_valid(self):
        form = RecipeSearchForm(data={}, ingredient_choices=[])
        self.assertTrue(form.is_valid())


# ---------------------------------------------
# URL CONFIGURATION TESTS
# ---------------------------------------------
class URLTests(TestCase):

    def test_urls_resolve(self):
        self.assertEqual(resolve(reverse("recipes:recipes_home")).func, recipes_home)
        self.assertEqual(resolve(reverse("recipes:recipes_overview")).func.view_class, RecipeListView)
        self.assertEqual(resolve(reverse("recipes:recipe_charts")).func.view_class, ChartView)
