from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from app.models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower() == 'admin':
            raise forms.ValidationError("Login with name 'admin' is prohibited.")

        return username

    def clean(self):
        cleaned_data = super().clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_info = authenticate(request=None, username=username, password=password)

            if self.user_info is None:
                raise forms.ValidationError("Incorrect login or password.")

            if not self.user_info.is_active:
                raise forms.ValidationError("User is not active")

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_info', None)

class RegisterForm(forms.Form):
    username = forms.CharField(min_length=4, max_length=100, label="Username")
    email = forms.EmailField(label="Email")
    nick_name = forms.CharField(min_length=4, max_length=100, label="NickName")
    password = forms.CharField(min_length=8, widget=forms.PasswordInput, label="Password")
    repeat_password = forms.CharField(min_length=8, widget=forms.PasswordInput, label="Repeat Password")
    avatar = forms.ImageField(required=False, label="Avatar")

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this login already exists")
        return username

    def clean_nick_name(self):
        nick_name = self.cleaned_data.get('nick_name')

        if Profile.objects.filter(nick_name=nick_name).exists():
            raise forms.ValidationError("User with this nick name already exists")

        return nick_name

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("User with this email already exists")

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')

        if password is None:
            raise forms.ValidationError("Incorrect password")

        if repeat_password is None:
            raise forms.ValidationError("Incorrect repeating passsword")

        if password != repeat_password:
            raise forms.ValidationError("Passwords do not match")


class SettingsForm(forms.Form):
    username = forms.CharField(required=False, max_length=100, label="Username")
    email = forms.EmailField(required=False, label="Email")
    nick_name = forms.CharField(required=False, max_length=100, label="NickName")
    avatar = forms.ImageField(required=False,label="Avatar")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username.lower() == 'admin':
            raise forms.ValidationError("Login with name 'admin' is prohibited.")

        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("User with this login already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("User with this email already exists")

        return email

    def clean_nick_name(self):
        nick_name = self.cleaned_data.get('nick_name')

        if Profile.objects.filter(nick_name=nick_name).exclude(user=self.user).exists():
            raise forms.ValidationError("User with this nick name already exists")

        return nick_name

class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, label="Title")
    text = forms.CharField(required=False ,label="Text")
    tags = forms.CharField(required=False, label="Tags")

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags')

        if not tags_str:
            return []

        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        tags_list = list(set(tags_list))

        for tag in tags_list:
            if len(tag) > 20:
                raise forms.ValidationError(f"Tag '{tag}' is too long (max 20 chars)")

        return tags_list

class AnswerForm(forms.Form):
    text = forms.CharField(label="Text")

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if len(text) < 10:
            raise forms.ValidationError("Your answer is too small (min 10 chars)")

        return text
