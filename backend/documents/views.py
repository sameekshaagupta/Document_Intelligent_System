from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Document, DocumentChunk
from .serializers import DocumentSerializer, QuestionSerializer
from .rag_engine import RAGEngine
import os

rag_engine = RAGEngine()

@api_view(['GET'])
def get_documents(request):
    """Retrieve all documents"""
    documents = Document.objects.all().order_by('-created_at')
    serializer = DocumentSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def upload_document(request):
    """Upload and process document"""
    try:
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get file info
        file_name = file.name
        file_type = file_name.split('.')[-1].lower()
        file_size = file.size
        
        # Validate file type
        allowed_types = ['txt', 'pdf', 'docx', 'doc']
        if file_type not in allowed_types:
            return Response(
                {'error': f'File type {file_type} not supported. Allowed types: {allowed_types}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save document
        document = Document.objects.create(
            title=file_name,
            file_path=file,
            file_type=file_type,
            file_size=file_size,
            processing_status='pending'
        )
        
        # Process document asynchronously (in production, use Celery)
        try:
            rag_engine.process_document(document)
        except Exception as e:
            return Response(
                {'error': f'Processing failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def ask_question(request):
    """Ask question about document"""
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        document_id = serializer.validated_data['document_id']
        question = serializer.validated_data['question']
        num_chunks = serializer.validated_data['num_chunks']
        
        try:
            document = Document.objects.get(id=document_id)
            if document.processing_status != 'completed':
                return Response(
                    {'error': 'Document is still processing'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = rag_engine.query_documents(document_id, question, num_chunks)
            return Response({
                'question': question,
                'answer': result,
                'document_title': document.title
            })
            
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)