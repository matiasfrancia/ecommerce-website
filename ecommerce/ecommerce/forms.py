from django import forms

class EmailForm(forms.Form):
    asunto = forms.CharField(max_length=200)
    email = forms.EmailField()
    mensaje = forms.CharField(widget=forms.Textarea)