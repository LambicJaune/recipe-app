from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Recipe
from .views import recipes_home, RecipeListView, RecipeDetailView, ChartView
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image
import tempfile
import shutil
from .forms import RecipeCreateForm
from django.contrib.auth import get_user_model

"""
Tests for the recipes app.

Includes:
- View tests (Home, Overview, Detail, Charts, About, Recipe Create, Recipe Search, User Profile)
- Model tests
- Form tests (RecipeSearchForm, RecipeCreateForm)
- Authentication tests (signup, login, logout)
"""

# ---------------------------------------------
# Helper functions
# ---------------------------------------------
def get_dummy_image():

    """Returns a simple in-memory PNG image for testing."""
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), "white")
    image.save(file, "PNG")
    file.seek(0)
    return SimpleUploadedFile("test.png", file.read(), content_type="image/png")

def create_recipe(name="Test Recipe", cooking_time=20, ingredients="Eggs\nMilk", pic=None):
    if pic is None:
        pic = get_dummy_image()
    return Recipe.objects.create(
        name=name,
        cooking_time=cooking_time,
        ingredients=ingredients,
        pic=pic
    )

# ---------------------------------------------
# Base Test Class with Temporary MEDIA_ROOT
# ---------------------------------------------
class MediaTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls._temp_media)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls._temp_media)
        super().tearDownClass()

# ---------------------------------------------
# HOME VIEW TESTS
# ---------------------------------------------
class HomeViewTests(MediaTestCase):

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
class LoginRequiredTests(MediaTestCase):

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
class RecipeListViewTests(MediaTestCase):

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
class RecipeDetailViewTests(MediaTestCase):

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
class ChartViewTests(MediaTestCase):

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
from .forms import RecipeSearchForm, RecipeCreateForm

class RecipeSearchFormTests(MediaTestCase):

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

class RecipeCreateFormTests(MediaTestCase):

    def test_valid_form(self):
        form = RecipeCreateForm(data={
            "name": "My Recipe",
            "ingredients": "Eggs, Milk",
            "cooking_time": 10
        })
        self.assertTrue(form.is_valid())

    def test_negative_cooking_time_is_invalid(self):
        form = RecipeCreateForm(data={
            "name": "Bad Recipe",
            "ingredients": "Nothing",
            "cooking_time": -1
        })
        self.assertFalse(form.is_valid())
        self.assertIn("cooking_time", form.errors)

    def test_ingredients_are_normalized(self):
        form = RecipeCreateForm(data={
            "name": "Normalize Test",
            "ingredients": "Eggs\nMilk ,  Sugar",
            "cooking_time": 5
        })
        self.assertTrue(form.is_valid())
        recipe = form.save()
        self.assertEqual(recipe.ingredients, "Eggs, Milk, Sugar")

# ---------------------------------------------
# URL CONFIGURATION TESTS
# ---------------------------------------------
class URLTests(MediaTestCase):

    def test_urls_resolve(self):
        self.assertEqual(resolve(reverse("recipes:recipes_home")).func, recipes_home)
        self.assertEqual(resolve(reverse("recipes:recipes_overview")).func.view_class, RecipeListView)
        self.assertEqual(resolve(reverse("recipes:recipe_charts")).func.view_class, ChartView)

User = get_user_model()


# ---------------------------------------------
# ABOUT VIEW TESTS
# ---------------------------------------------
class AboutViewTests(MediaTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="pass123")
        self.client.login(username="tester", password="pass123")

    def test_about_page_loads(self):
        response = self.client.get(reverse("recipes:about_the_dev"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/about_the_dev.html")
        self.assertIn("developer", response.context)


# ---------------------------------------------
# RECIPE CREATE VIEW TESTS
# ---------------------------------------------
class RecipeCreateViewTests(MediaTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("creator", password="pass123")
        self.client.login(username="creator", password="pass123")

    def test_create_view_get(self):
        response = self.client.get(reverse("recipes:recipe_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_create.html")
        self.assertIsInstance(response.context["form"], RecipeCreateForm)

    def test_create_recipe_valid_post(self):
        response = self.client.post(
            reverse("recipes:recipe_create"),
            {
                "name": "New Recipe",
                "ingredients": "Eggs, Milk",
                "cooking_time": 15,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Recipe.objects.filter(name="New Recipe").exists())

    def test_create_recipe_invalid_post(self):
        response = self.client.post(
            reverse("recipes:recipe_create"),
            {
                "name": "",
                "ingredients": "",
                "cooking_time": -5,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Recipe.objects.count(), 0)


# ---------------------------------------------
# RECIPE SEARCH VIEW (DEDICATED)
# ---------------------------------------------
class RecipeSearchViewTests(MediaTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("searcher", password="pass123")
        self.client.login(username="searcher", password="pass123")

        create_recipe("Apple Pie", 25, "Apple\nSugar")
        create_recipe("Egg Salad", 5, "Eggs\nSalt")

    def test_search_page_loads(self):
        response = self.client.get(reverse("recipes:recipe_search"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipe_search.html")

    def test_search_by_name(self):
        response = self.client.get(
            reverse("recipes:recipe_search"),
            {"recipe_name": "apple"},
        )
        self.assertContains(response, "Apple Pie")
        self.assertNotContains(response, "Egg Salad")

    def test_search_no_results(self):
        response = self.client.get(
            reverse("recipes:recipe_search"),
            {"recipe_name": "doesnotexist"},
        )
        self.assertNotContains(response, "Apple Pie")
        self.assertNotContains(response, "Egg Salad")


# ---------------------------------------------
# USER PROFILE VIEW TESTS
# ---------------------------------------------
class UserProfileViewTests(MediaTestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="profileuser",
            password="oldpassword",
            email="old@test.com",
        )
        self.client.login(username="profileuser", password="oldpassword")

    def test_profile_page_loads(self):
        response = self.client.get(reverse("recipes:user_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/user.html")

    def test_profile_update(self):
        response = self.client.post(
            reverse("recipes:user_profile"),
            {
                "update_profile": "1",
                "username": "profileuser",
                "email": "new@test.com",
                "first_name": "New",
                "last_name": "Name",
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@test.com")

    def test_password_change_success(self):
        response = self.client.post(
            reverse("recipes:user_profile"),
            {
                "change_password": "1",
                "old_password": "oldpassword",
                "new_password1": "NewStrongPass123",
                "new_password2": "NewStrongPass123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.client.login(
                username="profileuser", password="NewStrongPass123"
            )
        )

    def test_password_change_failure(self):
        response = self.client.post(
            reverse("recipes:user_profile"),
            {
                "change_password": "1",
                "old_password": "wrongpassword",
                "new_password1": "x",
                "new_password2": "y",
            },
        )
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------
# AUTH VIEWS (PROJECT LEVEL)
# ---------------------------------------------
class AuthViewTests(MediaTestCase):

    def setUp(self):
        self.client = Client()

    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/signup.html")

    def test_signup_creates_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=True,
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_success(self):
        User.objects.create_user("loginuser", password="pass123")
        response = self.client.post(
            reverse("login"),
            {
                "username": "loginuser",
                "password": "pass123",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "wrong",
                "password": "wrong",
            },
        )
        self.assertContains(response, "ooops")

    def test_logout_redirects(self):
        user = User.objects.create_user("logoutuser", password="pass123")
        self.client.login(username="logoutuser", password="pass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

# ---------------------------------------------
# MODEL TESTS
# ---------------------------------------------

class RecipeModelTests(MediaTestCase):

    def test_str_representation(self):
        recipe = Recipe.objects.create(
            name="chocolate cake",
            ingredients="Sugar, Cocoa",
            cooking_time=30
        )
        self.assertEqual(str(recipe), "Chocolate Cake")

    def test_name_and_ingredients_are_capitalized_on_save(self):
        recipe = Recipe.objects.create(
            name="apple pie",
            ingredients="apple\nsugar, flour",
            cooking_time=20
        )
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Apple Pie")
        self.assertEqual(recipe.ingredients, "Apple, Sugar, Flour")

    def test_calculate_difficulty_easy(self):
        recipe = Recipe.objects.create(
            name="Toast",
            ingredients="Bread, Butter",
            cooking_time=5
        )
        self.assertEqual(recipe.calculate_difficulty, "Easy")

    def test_calculate_difficulty_medium(self):
        recipe = Recipe.objects.create(
            name="Salad",
            ingredients="Lettuce, Tomato, Onion, Oil",
            cooking_time=5
        )
        self.assertEqual(recipe.calculate_difficulty, "Medium")

    def test_calculate_difficulty_intermediate(self):
        recipe = Recipe.objects.create(
            name="Pasta",
            ingredients="Pasta, Salt, Oil",
            cooking_time=15
        )
        self.assertEqual(recipe.calculate_difficulty, "Intermediate")

    def test_calculate_difficulty_hard(self):
        recipe = Recipe.objects.create(
            name="Complex Dish",
            ingredients="A, B, C, D, E, F, G",
            cooking_time=45
        )
        self.assertEqual(recipe.calculate_difficulty, "Hard")

    def test_pic_or_default_returns_default_when_missing(self):
        recipe = Recipe.objects.create(
            name="No Pic",
            ingredients="Water",
            cooking_time=1
        )
        self.assertIn("no_picture.jpg", recipe.pic_or_default)

    def test_get_absolute_url(self):
        recipe = Recipe.objects.create(
            name="URL Test",
            ingredients="Test",
            cooking_time=10
        )
        self.assertEqual(
            recipe.get_absolute_url(),
            reverse("recipes:recipe_detail", kwargs={"pk": recipe.pk})
        )

