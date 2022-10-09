from django.forms import ModelForm
from . import models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class Form(ModelForm):

    class Meta:
        model = models.Document
        fields = (
            'docfile',
        )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]
