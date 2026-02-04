from django import forms
from .models import Recipe
from django.contrib.auth.models import User

# Overview search form
class RecipeSearchForm(forms.Form):
    """
    Form for searching recipes based on various criteria.
    """
    recipe_name = forms.CharField(
        label='Recipe Name',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-item', 'placeholder': 'Enter a recipe name'})
    )
    
    ingredient = forms.MultipleChoiceField(
        label='Ingredient(s)',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'dropdown-checkbox-list'}),
        choices=[],
    )
    
    difficulty_level = forms.ChoiceField(
        label='Difficulty Level',
        choices=[
            ('', 'Any'),
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('intermediate', 'Intermediate'),
            ('hard', 'Hard')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-item'})
    )
    
    max_cooking_time = forms.IntegerField(
        label='Max Cooking Time (mn)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-item', 'placeholder': 'e.g., 30'})
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and dynamically set ingredient choices.
        """
        ingredient_choices = kwargs.pop('ingredient_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].choices = ingredient_choices

    def clean(self):
        """
        Custom validation for the form.
        Warn if 'hard' difficulty is selected with max cooking time less than 30 minutes.
        """
        cleaned_data = super().clean()
        difficulty = cleaned_data.get("difficulty_level")
        max_time = cleaned_data.get("max_cooking_time")

        # Warning but do not block form
        if difficulty == "hard" and (max_time is not None and max_time < 30):
            self.add_error(None, "Hard recipes must take at least 30 minutes.")  # non-field error

        return cleaned_data

class RecipeCreateForm(forms.ModelForm):
    """
    Form used to create and validate a new recipe.
    """
    class Meta:
        model = Recipe
        fields = ['name', 'ingredients', 'cooking_time', 'pic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-item', 'placeholder': 'Enter recipe name'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-item', 'placeholder': 'Enter ingredients, separated by commas', 'rows': 5}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-item', 'placeholder': 'Minutes, can be 0'}),
        }

    def clean_ingredients(self):
        """
        Clean and format the ingredients field.
        Replaces newlines with commas and normalizes spacing.
        """
        ingredients = self.cleaned_data.get('ingredients', '')

        # Replace newlines with commas
        ingredients = ingredients.replace('\n', ',')

        # Normalize spacing
        ingredients = ', '.join(
            part.strip() for part in ingredients.split(',') if part.strip()
        )

        return ingredients


    def clean_cooking_time(self):
        """
        Ensure cooking time is non-negative.
        """
        time = self.cleaned_data.get('cooking_time')
        if time is None or time < 0:
            raise forms.ValidationError("Cooking time cannot be negative.")
        return time

# Chart form, used only in recipe_charts view
CHART_CHOICES = (
   ('Bar', 'Bar chart'),
   ('Pie', 'Pie chart'),
   ('Line', 'Line chart')
)

class ChartForm(forms.Form):
    """
    Form for selecting chart type to display recipe statistics.
    """
    chart_type = forms.ChoiceField(
        label='Chart Type',
        choices=CHART_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-item'})
    )

class CustomUserChangeForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]