from django import forms

class VideoUploadForm(forms.Form):
    video = forms.FileField(label='Upload a Video')

class MediaUploadForm(forms.Form):
    video = forms.FileField()
