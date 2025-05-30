from rest_framework import serializers
from .models import Document, DocumentChunk

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = '__all__'

class QuestionSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    question = serializers.CharField(max_length=1000)
    num_chunks = serializers.IntegerField(default=3, min_value=1, max_value=10)