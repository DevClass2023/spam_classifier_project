from django import forms
from .models import ClassificationFeedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = ClassificationFeedback
        fields = ['is_correct', 'user_comment']
        widgets = {
            'user_comment': forms.Textarea(attrs={'rows': 3}),
        }