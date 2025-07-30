from django import forms
from .models import NewsPost


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ["title", "content", "is_active"]
        labels = {
            "title": "Заглавие",
            "content": "Съдържание",
            "is_active": "Активна новина",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["content"].widget.attrs.update({"class": "form-control"})
        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})
