from dict.models import Word, Category
from django import forms


class CreatePostForm(forms.ModelForm):
    eng = forms.CharField(widget=forms.TextInput, label='английское значение')
    rus = forms.CharField(widget=forms.TextInput, label='перевод', required=False)
    description = forms.CharField(widget=forms.TextInput, label='описание', required=False)
    association = forms.CharField(widget=forms.TextInput, label='ассоциация', required=False)
    category = forms.ModelMultipleChoiceField(queryset=None)


    class Meta:
        model = Word
        fields = (
            'eng',
            'rus',
            'description',
            'association',
            'category'
        )


class SelectCategoryForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=None,
        # widget=forms.CheckboxSelectMultiple
    )
