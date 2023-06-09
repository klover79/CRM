from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class AgentModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

class AgentUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields ={
            'email',
            'first_name',
            'last_name',
            'username',
        }

        field_order = ['email','first_name','last_name', 'username',]
