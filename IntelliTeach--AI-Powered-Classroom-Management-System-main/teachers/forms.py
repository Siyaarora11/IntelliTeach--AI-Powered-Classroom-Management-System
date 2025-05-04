# forms.py
from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    template_name = 'widgets/multiple_file_input.html'  # Provide the path to your custom template

class AssignmentUpdateForm(forms.Form):
    title = forms.CharField(max_length=500, required=True)
    description = forms.CharField(widget=forms.Textarea, required=False)
    due_date = forms.DateTimeField(required=True, input_formats=['%Y-%m-%dT%H:%M'])
    attachments = forms.FileField(required=False, widget=forms.ClearableFileInput)
    question_titles = forms.CharField(required=False)
    question_descriptions = forms.CharField(widget=forms.Textarea, required=False)
    question_attachments = forms.FileField(required=False, widget=MultipleFileInput)
