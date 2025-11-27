from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from .models import Recipe

# ------------------------------------------------------
# MODEL TESTS
# ------------------------------------------------------
class RecipeModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.recipe = Recipe.objects.create(
            name="Pancakes",
            ingredients="Flour\nEggs\nMilk",
            cooking_time=15
        )

    def test_name_label(self):
        field_label = self.recipe._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        field = self.recipe._meta.get_field('name')
        self.assertEqual(field.max_length, 120)

    def test_ingredients_is_textfield(self):
        field_type = self.recipe._meta.get_field('ingredients').get_internal_type()
        self.assertEqual(field_type, 'TextField')

    def test_difficulty_max_length(self):
        field = self.recipe._meta.get_field('difficulty')
        self.assertEqual(field.max_length, 20)

    def test_difficulty_non_editable(self):
        field = self.recipe._meta.get_field('difficulty')
        self.assertFalse(field.editable)

    def test_str_method(self):
        self.assertEqual(str(self.recipe), "Pancakes")

    def test_get_absolute_url(self):
        url = self.recipe.get_absolute_url()
        expected = reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk})
        self.assertEqual(url, expected)

    # ------------------------------
    # Difficulty calculation tests
    # ------------------------------
    def test_calculate_difficulty_easy(self):
        recipe = Recipe(name="Test", ingredients="A\nB", cooking_time=5)
        self.assertEqual(recipe.calculate_difficulty(), "Easy")

    def test_calculate_difficulty_medium(self):
        recipe = Recipe(name="Test", ingredients="A\nB\nC\nD", cooking_time=5)
        self.assertEqual(recipe.calculate_difficulty(), "Medium")

    def test_calculate_difficulty_intermediate(self):
        recipe = Recipe(name="Test", ingredients="A\nB", cooking_time=15)
        self.assertEqual(recipe.calculate_difficulty(), "Intermediate")

    def test_calculate_difficulty_hard(self):
        recipe = Recipe(name="Test", ingredients="A\nB\nC\nD", cooking_time=20)
        self.assertEqual(recipe.calculate_difficulty(), "Hard")

    def test_difficulty_saved_on_save(self):
        recipe = Recipe.objects.create(
            name="Toast",
            ingredients="Bread",
            cooking_time=1
        )
        self.assertEqual(recipe.difficulty, "Easy")

    # ------------------------------
    # Image field default
    # ------------------------------
    def test_default_image(self):
        recipe = Recipe(name="NoPic", ingredients="A", cooking_time=1)
        recipe.save()
        self.assertEqual(recipe.pic.name, "no_picture.jpg")


# ------------------------------------------------------
# VIEW TESTS
# ------------------------------------------------------
class RecipeListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(3):
            Recipe.objects.create(
                name=f"Recipe {i}",
                ingredients="A\nB\nC",
                cooking_time=10
            )

    def test_list_view_status_code(self):
        response = self.client.get(reverse('recipes:recipes_overview'))
        self.assertEqual(response.status_code, 200)

    def test_list_view_template_used(self):
        response = self.client.get(reverse('recipes:recipes_overview'))
        self.assertTemplateUsed(response, 'recipes/recipes_overview.html')

    def test_list_view_context_name(self):
        response = self.client.get(reverse('recipes:recipes_overview'))
        self.assertIn('recipes', response.context)

    def test_list_view_contains_recipes(self):
        response = self.client.get(reverse('recipes:recipes_overview'))
        self.assertEqual(len(response.context['recipes']), 3)


class RecipeDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.recipe = Recipe.objects.create(
            name="Pizza",
            ingredients="Cheese\nTomato",
            cooking_time=20
        )

    def test_detail_view_status_code(self):
        response = self.client.get(reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_template(self):
        response = self.client.get(reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk}))
        self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

    def test_detail_view_context_name(self):
        response = self.client.get(reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk}))
        self.assertIn('recipe', response.context)

    def test_detail_view_displays_name(self):
        response = self.client.get(reverse('recipes:recipe_detail', kwargs={'pk': self.recipe.pk}))
        self.assertContains(response, "Pizza")


# ------------------------------------------------------
# HOME VIEW
# ------------------------------------------------------
class HomeViewTest(TestCase):

    def test_home_status_code(self):
        response = self.client.get(reverse('recipes:recipes_home'))
        self.assertEqual(response.status_code, 200)

    def test_home_template(self):
        response = self.client.get(reverse('recipes:recipes_home'))
        self.assertTemplateUsed(response, 'recipes/recipes_home.html')

    def test_home_contains_title(self):
        response = self.client.get(reverse('recipes:recipes_home'))
        self.assertContains(response, "WELCOME TO THE RECIPE APP")


# ------------------------------------------------------
# URL TESTS
# ------------------------------------------------------
class URLTests(TestCase):

    def test_overview_url_resolves(self):
        response = self.client.get('/overview/')
        self.assertEqual(response.status_code, 200)

    def test_home_url_resolves(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
