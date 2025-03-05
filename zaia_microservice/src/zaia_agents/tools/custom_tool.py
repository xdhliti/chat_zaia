import base64
import io
import fitz  # PyMuPDF
from crewai.tools import BaseTool
from typing import Any, Optional, Type
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader


class FReadTool(BaseTool):
    """A tool for reading PDF content, decoding it from base64 if needed."""

    name: str = "Read a PDF file's content"
    description: str = "A tool that reads the content of a PDF file. Provide 'file_path' or 'file_content_b64' parameter."
    pdf_path: Optional[str] = None

    def _run(self) -> str:
        reader = PdfReader(self.pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
