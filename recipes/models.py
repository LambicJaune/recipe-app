from django.db import models
from django.shortcuts import reverse

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    ingredients = models.TextField()
    cooking_time = models.IntegerField(help_text="in minutes")
    difficulty = models.CharField(max_length=20, editable=False, blank=True)
    pic = models.ImageField(upload_to='recipes', default='no_picture.jpg')

    @property
    def calculate_difficulty(self):
        """Compute difficulty dynamically."""
        ingredients_list = [i.strip() for i in self.ingredients.splitlines() if i.strip()]

        if self.cooking_time < 10 and len(ingredients_list) < 4:
            return "Easy"
        elif self.cooking_time < 10 and len(ingredients_list) >= 4:
            return "Medium"
        elif self.cooking_time >= 10 and len(ingredients_list) < 4:
            return "Intermediate"
        else:
            return "Hard"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("recipes:recipe_detail", kwargs={"pk": self.pk})
