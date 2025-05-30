import os
import re
import chromadb
from sentence_transformers import SentenceTransformer
import openai
from django.conf import settings
from .models import Document, DocumentChunk
import PyPDF2
from docx import Document as DocxDocument
import fitz  # PyMuPDF - better PDF extraction
from pdfplumber import PDF  # Alternative PDF library


class RAGEngine:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="documents")

        # Setup OpenAI or LM Studio
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            openai.api_base = settings.LM_STUDIO_BASE_URL
            openai.api_key = "lm-studio"

    def clean_extracted_text(self, text):
        """Clean and normalize extracted text"""
        if not text:
            return ""

        replacements = {
            '♂': '',
            '♀': '',
            '⌢': '',
            '/envel⌢pe': ' | Email: ',
            '/linkedin': ' | LinkedIn: ',
            '/github': ' | GitHub: ',
            '  +': ' ',
            '\n\n\n': '\n\n',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r'phone\+(\d+)', r'Phone: +\1', text)
        text = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r' \1 ', text)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def extract_text_from_file(self, file_path, file_type):
        """Extract text content from different file formats with better quality"""
        text = ""
        pages_count = 1

        try:
            if file_type.lower() == 'txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                pages_count = 1

            elif file_type.lower() == 'pdf':
                text = self.extract_pdf_text_advanced(file_path)
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pages_count = len(pdf_reader.pages)

            elif file_type.lower() in ['docx', 'doc']:
                doc = DocxDocument(file_path)
                pages_count = 1
                paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
                text = '\n\n'.join(paragraphs)

        except Exception as e:
            print(f"Error extracting text: {str(e)}")

        text = self.clean_extracted_text(text)
        return text, pages_count

    def extract_pdf_text_advanced(self, file_path):
        """Advanced PDF text extraction using multiple methods"""
        text = ""

        try:
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            if text.strip():
                return text
        except ImportError:
            print("PyMuPDF not installed, falling back to PyPDF2")
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")

        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except ImportError:
            print("pdfplumber not installed, falling back to PyPDF2")
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")

        return text

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """Split text into meaningful chunks with better handling"""
        text = text.strip()
        if not text:
            return []

        sections = self.split_by_sections(text)
        if len(sections) > 1:
            return self.chunk_sections(sections, chunk_size, overlap)

        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def split_by_sections(self, text):
        """Split resume/document by logical sections"""
        section_patterns = [
            r'\b(Education|EDUCATION)\b',
            r'\b(Experience|EXPERIENCE|Work Experience)\b',
            r'\b(Skills|SKILLS|Technical Skills)\b',
            r'\b(Projects|PROJECTS)\b',
            r'\b(Certifications|CERTIFICATIONS)\b',
            r'\b(Awards|AWARDS|Achievements)\b',
        ]

        sections = []
        current_section = ""
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            is_section_header = any(re.search(pattern, line, re.IGNORECASE) for pattern in section_patterns)

            if is_section_header and current_section:
                sections.append(current_section.strip())
                current_section = line + "\n"
            else:
                current_section += line + "\n"

        if current_section.strip():
            sections.append(current_section.strip())

        return sections if len(sections) > 1 else [text]

    def chunk_sections(self, sections, chunk_size, overlap):
        """Chunk sections intelligently"""
        chunks = []

        for section in sections:
            if len(section) <= chunk_size:
                chunks.append(section)
            else:
                section_chunks = self.chunk_text_simple(section, chunk_size, overlap)
                chunks.extend(section_chunks)

        return chunks

    def chunk_text_simple(self, text, chunk_size, overlap):
        """Simple text chunking for large sections"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def process_document(self, document):
        """Process document and create embeddings"""
        try:
            document.processing_status = 'processing'
            document.save()

            text, pages_count = self.extract_text_from_file(
                document.file_path.path,
                document.file_type
            )

            if not text.strip():
                document.processing_status = 'failed'
                document.save()
                raise Exception("No text content found in document")

            document.pages_count = pages_count
            document.save()

            chunks = self.chunk_text(text)

            if not chunks:
                document.processing_status = 'failed'
                document.save()
                raise Exception("No chunks created from document")

            for i, chunk_text in enumerate(chunks):
                embedding = self.embedding_model.encode([chunk_text])[0]
                chunk_id = f"doc_{document.id}_chunk_{i}"

                metadata = {
                    "document_id": document.id,
                    "chunk_index": i,
                    "document_title": document.title
                }

                self.collection.add(
                    embeddings=[embedding.tolist()],
                    documents=[chunk_text],
                    ids=[chunk_id],
                    metadatas=[metadata]
                )

                DocumentChunk.objects.create(
                    document=document,
                    chunk_index=i,
                    text_content=chunk_text,
                    page_number=1,
                    embedding_id=chunk_id
                )

            document.processing_status = 'completed'
            document.save()

        except Exception as e:
            document.processing_status = 'failed'
            document.save()
            print(f"Error processing document: {str(e)}")
            raise e

    def query_documents(self, document_id, question, num_chunks=3):
        """Query document using RAG pipeline"""
        try:
            question_embedding = self.embedding_model.encode([question])[0]

            try:
                document = Document.objects.get(id=document_id)
                if document.processing_status != 'completed':
                    return f"Document is not ready. Status: {document.processing_status}"
            except Document.DoesNotExist:
                return "Document not found."

            chunk_count = document.chunks.count()
            if chunk_count == 0:
                return "No chunks found for this document."

            try:
                results = self.collection.query(
                    query_embeddings=[question_embedding.tolist()],
                    n_results=min(num_chunks, chunk_count),
                    where={"document_id": document_id}
                )
            except Exception as e:
                print(f"ChromaDB query error: {str(e)}")
                results = self.collection.query(
                    query_embeddings=[question_embedding.tolist()],
                    n_results=min(num_chunks, chunk_count)
                )

            if not results['documents'] or not results['documents'][0]:
                return "No relevant information found in the document."

            context = "\n\n".join(results['documents'][0])

            prompt = f"""Based on the following context from the document, answer the question accurately and concisely.

Context:
{context}

Question: {question}

Answer:"""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                answer = response.choices[0].message.content
            except Exception as llm_error:
                print(f"LLM error: {str(llm_error)}")
                answer = f"Based on the document content: {context[:300]}..."

            return {
                'answer': answer,
                'context': results['documents'][0],
                'sources': [f"Chunk {i+1}" for i in range(len(results['documents'][0]))],
                'document_title': document.title
            }

        except Exception as e:
            print(f"Query error: {str(e)}")
            return f"Error processing query: {str(e)}"
