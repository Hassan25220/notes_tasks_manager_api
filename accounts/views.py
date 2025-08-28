from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer, TaskSerializer, NoteSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from .models import Task, Note
from rest_framework.permissions import IsAuthenticated


# Create your views here.


# ------------------- AUTH ---------------------

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password= password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            })
        return Response({"error": "Invalid Credentials"}, status = HTTP_400_BAD_REQUEST)
    

# ---------------- TASK CRUD -------------------

# List + Create Tasks

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 🔹 List ke liye: sirf current user ke tasks return honge
    def get_queryset(self):
        return Task.objects.filter(user = self.request.user)
    
    # Assign the logged-in user to the task before saving (because read_only task user)
    def perform_create(self, serializer):
        serializer.save(user= self.request.user)


# Retrieve + Update + Delete Single Task

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    

# ------------- Note CRUD ------------------
class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    

# ----------- OPENAI Note Suggestion ---------------
import openai
from django.conf import settings
import traceback


class GenerateNoteFromTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")

        if not title or not description:
            return Response({"error": "Title and description are required."}, status=HTTP_400_BAD_REQUEST)

        try:
            # ✅ Use new OpenAI client
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            print("OPENAI_API_KEY:", settings.OPENAI_API_KEY)

            prompt = f"Suggest a note or summary for a task titled '{title}' with the description: '{description}'"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that suggests notes for project tasks."},
                    {"role": "user", "content": prompt}
                ]
            )

            note_suggestion = response.choices[0].message.content.strip()
            return Response({"suggested_note": note_suggestion})

        except Exception as e:
            print("Exception occurred in suggest-note endpoint:")
            traceback.print_exc()  # This will show full error
            return Response({"error": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)