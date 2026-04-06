from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'firebase_uid', 'text_preview', 'session_name', 'was_spoken', 'created_at']
    list_filter = ['was_spoken', 'session_name', 'created_at']
    search_fields = ['text', 'firebase_uid', 'session_name']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'Pregunta'
