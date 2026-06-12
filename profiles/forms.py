from django import forms
from .models import Profile, FeedbackEntry

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'visible', 'gender', 'seeking', 'birth_date',
            'studienfach', 'hochschule', 'regionen', 'sprachen',
            'quote', 'about', 'looking_for',
            'trinken', 'rauchen', 'interests', 'photo',
            'phone', 'prompts'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full border rounded p-2'}),
            'quote': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': 'Dein Spruch'}),
            'about': forms.Textarea(attrs={'rows': 4, 'class': 'w-full border rounded p-2', 'placeholder': 'Über dich...'}),
            'phone': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': '+49 170 1234567'}),
            'studienfach': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'hochschule': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'sprachen': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': 'z.B. Deutsch, Englisch'}),
            'regionen': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': 'z.B. ["Erfurt", "Berlin"]'}),
            'interests': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': 'z.B. ["Laufen", "Lesen"]'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'w-full border rounded p-2'}),
            'prompts': forms.Textarea(attrs={'rows': 4, 'class': 'w-full border rounded p-2', 'placeholder': '[{"q": "Frage", "a": "Antwort"}]'}),
        }

class FeedbackForm(forms.ModelForm):
    """Formular fuer Beta-Feedback, Bug-Reports und Feature-Wuensche."""
    class Meta:
        model = FeedbackEntry
        fields = ['typ', 'text']
        widgets = {
            'typ': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F9C513]'
            }),
            'text': forms.Textarea(attrs={
                'rows': 6,
                'class': 'w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#F9C513]',
                'placeholder': 'Beschreibe dein Anliegen, Bug oder Feature-Wunsch...'
            }),
        }
        labels = {
            'typ': 'Kategorie',
            'text': 'Deine Nachricht',
        }
