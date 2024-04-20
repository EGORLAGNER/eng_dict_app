from dict.models import Word
from django import forms


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = (
            'eng',
            'rus',
            'description',
        )
