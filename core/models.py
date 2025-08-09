from django.db import models
from django.contrib.auth.models import User


    
class EmailClassification(models.Model):
    """
    Stores the history of email classifications for each user.
    The 'user' field is now optional to support classifications from the Postfix script.
    """
    CLASSIFICATION_CHOICES = [
        ('ham', 'Ham'),
        ('spam', 'Spam'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_classifications', null=True, blank=True)
    email_text = models.TextField()
    classified_as = models.CharField(max_length=10, choices=CLASSIFICATION_CHOICES)
    prediction_confidence = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_feedback_provided = models.BooleanField(default=False)

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} - {self.classified_as} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        ordering = ['-timestamp']

class ClassificationFeedback(models.Model):
    """
    Stores feedback from users on specific classifications.
    """
    classification = models.OneToOneField(EmailClassification, on_delete=models.CASCADE, related_name='feedback')
    is_correct = models.BooleanField(help_text="Was the classification correct?")
    user_comment = models.TextField(blank=True, null=True, help_text="Optional comments from the user.")
    feedback_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.classification} - Correct: {self.is_correct}"

    class Meta:
        verbose_name_plural = "Classification Feedback"