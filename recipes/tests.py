from django.test import TestCase
from .models import Recipe
from django.db import models

# Create your tests here.

class myTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.recipe = Recipe.objects.create(name="Pancakes", ingredients="Flour, Eggs, Milk", cooking_time=15)
	
    def test_name_label(self):
        recipe = Recipe.objects.get(recipe_id=1)
        field_label = recipe._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        field = self.recipe._meta.get_field('name')
        self.assertEqual(field.max_length, 120)

    def test_ingredients_field_type(self):
        field = self.recipe._meta.get_field('ingredients')
        self.assertEqual(field.get_internal_type(), 'TextField')

    def test_difficulty_max_length(self):
        field = self.recipe._meta.get_field('difficulty')
        self.assertEqual(field.max_length, 20)

    def test_difficulty_not_editable(self):
        field = self.recipe._meta.get_field('difficulty')
        self.assertFalse(field.editable)

    def test_str_method_returns_name(self):
        self.assertEqual(str(self.recipe), "Pancakes")