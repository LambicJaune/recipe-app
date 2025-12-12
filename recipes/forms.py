from django import forms

# Overview search form
class RecipeSearchForm(forms.Form):
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
        label='Max Cooking Time (in minutes)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-item', 'placeholder': 'e.g., 30'})
    )

    def __init__(self, *args, **kwargs):
        ingredient_choices = kwargs.pop('ingredient_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].choices = ingredient_choices

    def clean(self):
        cleaned_data = super().clean()
        difficulty = cleaned_data.get("difficulty_level")
        max_time = cleaned_data.get("max_cooking_time")

        # Warning but do not block form
        if difficulty == "hard" and (max_time is not None and max_time < 30):
            self.add_error(None, "Hard recipes must take at least 30 minutes.")  # non-field error

        return cleaned_data


# Chart form, used only in recipe_charts view
CHART_CHOICES = (
   ('Bar', 'Bar chart'),
   ('Pie', 'Pie chart'),
   ('Line', 'Line chart')
)

class ChartForm(forms.Form):
    chart_type = forms.ChoiceField(
        label='Chart Type',
        choices=CHART_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-item'})
    )
