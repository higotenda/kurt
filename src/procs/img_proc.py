"""
A module to contain the image processor.
"""

import abcs
import logging
from procs.web_proc import head_content_type
from google.generativeai.types.content_types import mimetypes
import google.generativeai as genai
import requests
from typing import Optional
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__);

class ImgProc(abcs.MultimediaProc):
    """
    Processor for image-type multi-media.
    """

    sys_prompt = "What is in this image? Describe it to a person who is blind.";

    def __init__(self, api_key) -> None:
        self.api_key = api_key;

    # The function is called by KF Proc to handle individual keyframes.
    def raw(self, fp: str):
        """
        Internal.
        """
        img = Image.open(fp).convert("RGB")
        return "".join(
            p.text
            for p in self.model.generate_content([self.sys_prompt, img])
            .candidates[0]
            .content.parts
        )

    def consume(self, url: str, mime_type: Optional[str]=None):
        if mime_type is None:
            logger.warn("ImageProc not used in a mux. Fetching data.");
            mime_type = (head_content_type(url));

        if mime_type is None or (not mime_type.startswith("image/")):
            return None;

        logger.info("Configuring GenAi ImageProc.");
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro-vision")
        
        logger.info("ImgProc initialized.");
        
        response = requests.get(url)

        img = Image.open(BytesIO(response.content)).convert("RGB")
        a = "".join(
            p.text
            for p in self.model.generate_content([ImgProc.sys_prompt, img])
            .candidates[0]
            .content.parts
        )
        # ocr_output = ocr_string(img)
        # print("ocr_output: ", ocr_output)
        return abcs.Serialized(f"##<img url='{url}'>##{a}##</img>##");