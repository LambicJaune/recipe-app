from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from cloudinary_storage.storage import MediaCloudinaryStorage

class Recipe(models.Model):
    """
    Model representing a cooking recipe.
    """
    recipe_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    ingredients = models.TextField()
    cooking_time = models.IntegerField(help_text="in minutes")
    difficulty = models.CharField(max_length=20, editable=False, blank=True)
    pic = models.ImageField(upload_to='recipes', storage=MediaCloudinaryStorage(), default=None, blank=True, null=True)

    @property
    def calculate_difficulty(self):
        """
        Compute difficulty dynamically based on cooking time and number of ingredients.
        """
        ingredients_list = [i.strip() for i in self.ingredients.replace("\n", ",").split(',') if i.strip()]
        num_ingredients = len(ingredients_list)

        if self.cooking_time < 10 and num_ingredients < 4:
            return "Easy"
        elif self.cooking_time < 10 and num_ingredients >= 4:
            return "Medium"
        elif self.cooking_time >= 10 and num_ingredients <= 6:
            return "Intermediate"
        else:
            return "Hard"
        
    @property
    def pic_or_default(self):
        """
        Return the URL of the recipe picture or a default image if not available.
        """
        try:
            if self.pic and self.pic.name:
                return self.pic.url
        except ValueError:
            pass
        return static('recipes/images/no_picture.jpg')

    def save(self, *args, **kwargs):
        """
        Override save method to:
         - Set difficulty and format fields.
         - Capitalize recipe name 
         - Capitalize and normalize ingredients
         - Call superclass save method.
        """
        # Capitalize first letter of each word
        if self.name:
            self.name = self.name.title()

        # Capitalize each ingredient
        if self.ingredients:
            ingredients_list = [i.strip().title() for i in self.ingredients.replace("\n", ",").split(',')]
            self.ingredients = ', '.join(ingredients_list)

        super().save(*args, **kwargs)
        

    def __str__(self):
        """
        String representation of the Recipe model.
        """
        return self.name

    def get_absolute_url(self):
        """
        Get the URL to access a detail record for this recipe.
        """
        return reverse("recipes:recipe_detail", kwargs={"pk": self.pk})

