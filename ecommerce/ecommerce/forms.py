from django import forms

class EmailForm(forms.Form):
    asunto = forms.CharField(max_length=200)
    mensaje = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()