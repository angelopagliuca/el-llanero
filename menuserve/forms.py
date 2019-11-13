from django import forms
from .models import *

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('image', 'name', 'description', 'price', )

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('image', 'user', )

class LoginForm(forms.Form):
    username = forms.CharField(max_length=25)
    password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.Form):
	first_name = forms.CharField(max_length=50)
	last_name = forms.CharField(max_length=50)
	username = forms.CharField(max_length=50)
	password = forms.CharField(max_length=32, widget=forms.PasswordInput)
