from dict.models import Word
from django import forms


class CreateWordForm(forms.ModelForm):
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


class WordDetailForm(forms.ModelForm):
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


class SelectCategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        # widget=forms.CheckboxSelectMultiple
    )


class SelectDeleteWordForm(forms.Form):
    word = forms.CheckboxSelectMultiple()
