from django import forms
from django.contrib.auth.models import User
from .models import Profile, Item, BorrowTransaction

# --------- Sign Up Form ---------
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    department = forms.CharField(max_length=100)
    id_number = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'department', 'id_number']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

# --------- Optional: Edit User Form (if you want Django form handling) ---------
class EditUserForm(forms.ModelForm):
    department = forms.CharField(max_length=100)
    id_number = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'department', 'id_number']

# --------- Optional: Item Form (if you want Django form handling) ---------
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'item_type', 'serial_number', 'condition', 'stock']


class BorrowForm(forms.ModelForm):
    class Meta:
        model = BorrowTransaction
        fields = ['item', 'quantity']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['department', 'id_number', 'contact_number', 'profile_image']