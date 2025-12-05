from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Course, Lesson, Comment, Review


User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(
        choices=User.Roles.choices,
        label="Peran",
        help_text="Pilih 'Instruktur' jika Anda ingin membuat dan mengelola kursus.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "role")


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "category",
            "tags",
            "level",
            "thumbnail",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control wysiwyg", "rows": 8}),
            "short_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "order", "content", "video_url", "attachment", "is_preview"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control wysiwyg", "rows": 10}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Tulis komentar Anda..."}),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Rating",
    )

    class Meta:
        model = Review
        fields = ["rating", "content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Bagikan pengalaman Anda dengan kursus ini..."}
            ),
        }