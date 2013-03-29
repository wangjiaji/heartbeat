from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
import re

email_re = re.compile(r'[^@]+@[^@]+.[^@]')

class SignupForm(UserCreationForm):
    error_messages = {
        'duplicate_email': _('This email address has already been taken.'),
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    # Override since this function refers django's
    # default User model
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class LoginForm(AuthenticationForm):
    # Allow email login
    def clean(self):
        username = self.cleaned_data.get('username')
        if email_re.match(username):
            try:
                user = User.objects.only('username').get(email=username)
            except User.DoesNotExist:
                pass
            else:
                cleaned_data['username'] = user.username
        return super(LoginForm, self).clean()

class UserPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=64)

    def clean(self):
        uname = self.cleaned_data['username']
        if not uname in [user.username for user in self.users_cache]:
            raise forms.ValidationError('The username and email address do not match')
        return super(UserPasswordResetForm, self).clean()
