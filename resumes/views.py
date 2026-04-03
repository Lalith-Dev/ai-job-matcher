from rest_framework import generics, permissions
from .models import Resume
from .serializers import ResumeSerializer
from .utils import extract_text_from_pdf

class ResumeUploadView(generics.CreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file = self.request.FILES['file']
        text = extract_text_from_pdf(file)

        serializer.save(
            user=self.request.user,
            extracted_text=text
        )