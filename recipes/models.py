from django.db import models

# Create your models here.

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    ingredients = models.TextField()
    cooking_time = models.IntegerField(help_text='in minutes')
    difficulty = models.CharField(max_length=20, editable=False)

    def __str__(self):
        return self.name