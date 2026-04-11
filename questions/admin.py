from django.contrib import admin
from questions.entities.question_entity import Question
from questions.entities.video_entity import Video, Subtitle


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'firebase_uid', 'text_preview', 'session_name', 'was_spoken', 'created_at']
    list_filter = ['was_spoken', 'session_name', 'created_at']
    search_fields = ['text', 'firebase_uid', 'session_name']
    readonly_fields = ['created_at']

    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'Pregunta'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'firebase_uid', 'status', 'language', 'created_at']
    list_filter = ['status', 'language', 'created_at']
    search_fields = ['title', 'firebase_uid']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'video', 'index', 'start_time', 'end_time', 'text_preview', 'is_edited']
    list_filter = ['is_edited', 'video']
    search_fields = ['text']

    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Texto'
