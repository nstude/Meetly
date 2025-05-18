from django import forms

class AddFriendForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)