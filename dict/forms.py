from dict.models import Word, Category
from django import forms


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = (
            'eng',
            'rus',
            'description',
            'association',
            'category'
        )

        widgets = {
            'eng': forms.TextInput,
            'rus': forms.TextInput,
            'description': forms.TextInput,
            'association': forms.TextInput,
            'category': forms.CheckboxSelectMultiple,
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
            'description',
        )

        widgets = {
            'name': forms.TextInput,
            'description': forms.TextInput,
        }


class SelectCategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple
    )


class SelectDeleteWordForm(forms.Form):
    word = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple, label=None)
