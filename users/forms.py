from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
        for fieldname in ['password', 'password_confirm']:
            if fieldname in self.fields:
                self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
