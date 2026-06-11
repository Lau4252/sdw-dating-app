from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'study_program', 'city', 'birth_date', 'interests']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full border rounded p-2'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'study_program': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'city': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'interests': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2'}),
        }
