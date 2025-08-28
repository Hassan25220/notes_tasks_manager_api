from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)






urlpatterns = [
    # ----- AUTH -------
    path('register/', RegisterView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),

    # ----- TASKS -------
    path('tasks/', TaskListCreateView.as_view(), name = 'task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name = 'task-detail'),

    # ----- Notes ------
    path('notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]

urlpatterns += [
    path('tasks/suggest-note/', GenerateNoteFromTaskView.as_view(), name='suggest-note'),
]