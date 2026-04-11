from django.urls import path, include
from rest_framework.routers import DefaultRouter
from questions.views.question_view import QuestionViewSet
from questions.views.video_view import VideoViewSet, SubtitleViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'subtitles', SubtitleViewSet, basename='subtitle')

urlpatterns = [
    path('', include(router.urls)),
]
