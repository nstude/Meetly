from django import forms

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, required=True)
