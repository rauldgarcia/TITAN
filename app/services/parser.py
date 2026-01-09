import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SECParser:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalizes whitespace and removes non-printable characteres.
        """
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def clean_html(content: str) -> str:
        """
        Sophisticated HTML strategy for financial documents.
        """
        soup = BeautifulSoup(content, 'lxml')

        for tag in soup(["script", "style", "meta", "noscript", "head", "link"]):
            tag.extract()

        for table in soup.find_all("table"):
            table.insert_before("\n")
            table.insert_after("\n")

        text = soup.get_text(separator='\n')

        lines = []
        for line in text.splitlines():
            clean_line = line.strip()
            if clean_line and len(clean_line) > 1:
                lines.append(clean_line)
        
        return "\n".join(lines)