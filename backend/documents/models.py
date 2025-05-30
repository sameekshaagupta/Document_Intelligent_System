from django.db import models
from django.utils import timezone


class Document(models.Model):
    title = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10)
    file_size = models.IntegerField()
    pages_count = models.IntegerField(default=0)

    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.IntegerField()
    text_content = models.TextField()
    page_number = models.IntegerField(default=1)
    embedding_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('document', 'chunk_index')

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
