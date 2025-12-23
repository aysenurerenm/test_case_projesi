from django import forms

class UploadCodeForm(forms.Form):
    code = forms.CharField(widget=forms.Textarea, required=False)
    file = forms.FileField(required=False)
