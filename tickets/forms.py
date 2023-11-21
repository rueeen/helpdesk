from django import forms
from .models import Ticket, History, Tech

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class TechForm(forms.ModelForm):
    class Meta:
        model = Tech
        fields = ['name', 'last_name', 'avatar']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

class HistoryForm(forms.ModelForm):
    class Meta:
        model = History
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'})
        }
