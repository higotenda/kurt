"""
A module to implement webpage processor.
"""

from typing import Optional

import requests
from bs4 import BeautifulSoup
import abcs
# from impl.ocr import ocr_string
import logging

logger = logging.getLogger(__name__)

def head_content_type(url: str) -> Optional[str]:
    response = requests.head(url)
    if response.status_code != 200:
        logger.warn("Failed to load url. May have expired")
        return None;
    return response.headers.get("Content-Type")

class WebpageProc(abcs.MultimediaProc):

    def consume(self, url: str, mime_type=None):
        if mime_type is None:
            mime_type = head_content_type(url);

        if mime_type is None or (not mime_type.startswith("text/")):
            return None;    # Don't handle other stuff.

        logger.info(f"Making request for {url}.");

        response = requests.get(url)
        html_content = response.text

        logger.info("Extracting text.");
        
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()
        
        logger.info("Website parsed");
        
        return abcs.Serialized(f"##<article>##{text}##</article>");


