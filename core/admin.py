from django.contrib import admin
from .models import EmailClassification, ClassificationFeedback

@admin.register(EmailClassification)
class EmailClassificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'classified_as', 'prediction_confidence', 'timestamp', 'is_feedback_provided')
    list_filter = ('classified_as', 'is_feedback_provided', 'timestamp')
    search_fields = ('user__username', 'email_text')
    raw_id_fields = ('user',)

@admin.register(ClassificationFeedback)
class ClassificationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('classification', 'is_correct', 'feedback_timestamp')
    list_filter = ('is_correct', 'feedback_timestamp')
    search_fields = ('classification__email_text',)