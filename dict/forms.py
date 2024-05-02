from dict.models import Word, Category
from django import forms


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = (
            'eng',
            'rus',
            'description',
            'association',
        )


class SelectCategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        # widget=forms.CheckboxSelectMultiple
    )
