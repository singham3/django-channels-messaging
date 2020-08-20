from django import forms
from django.contrib.auth import get_user_model
from .models import *


class CreateUserForm(forms.Form):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    repeat_password = forms.CharField(required=True, widget=forms.PasswordInput())
    user_profile = forms.FileField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'repeat_password', 'user_profile')

    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")
        if password != repeat_password:
            raise forms.ValidationError("Password And Repeat Password Not Match")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username Already Exist")

        return cleaned_data
