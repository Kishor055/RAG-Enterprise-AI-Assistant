import os
from typing import List
from app.interfaces.document_parser import BaseDocumentParser, ParsedPage

class FileParser(BaseDocumentParser):
    def parse_file(self, file_path: str) -> List[ParsedPage]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext in [".txt", ".md", ".csv"]:
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _parse_pdf(self, file_path: str) -> List[ParsedPage]:
        pages = []
        # Try PyMuPDF (fitz) first, fallback to pypdf
        try:
            import fitz
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                text = doc[page_num].get_text("text")
                if text.strip():
                    pages.append(ParsedPage(page_number=page_num + 1, text=text.strip()))
            doc.close()
            if pages:
                return pages
        except Exception:
            pass

        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append(ParsedPage(page_number=idx + 1, text=text.strip()))
            return pages
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF file: {str(e)}")

    def _parse_docx(self, file_path: str) -> List[ParsedPage]:
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            # Group text into logical virtual pages (approx 1500 chars per page)
            pages = []
            chunk_size = 1500
            for i in range(0, len(full_text), chunk_size):
                page_text = full_text[i:i + chunk_size]
                pages.append(ParsedPage(page_number=(i // chunk_size) + 1, text=page_text))
            return pages if pages else [ParsedPage(page_number=1, text="")]
        except Exception as e:
            raise RuntimeError(f"Failed to parse DOCX file: {str(e)}")

    def _parse_text(self, file_path: str) -> List[ParsedPage]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            chunk_size = 1500
            pages = []
            for i in range(0, len(content), chunk_size):
                page_text = content[i:i + chunk_size]
                pages.append(ParsedPage(page_number=(i // chunk_size) + 1, text=page_text))
            return pages if pages else [ParsedPage(page_number=1, text="")]
        except Exception as e:
            raise RuntimeError(f"Failed to parse text file: {str(e)}")
