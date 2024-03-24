"""
A module to implement various multimedia processors.
"""

import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import abcs
import os
import requests
from io import BytesIO
import re
import infer
from impl.ocr import ocr_string
from PIL import Image
import impl.kf_proc
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

class ImgProc(abcs.MultimediaProc):
    """
    Processor for image-type multi-media.
    """

    def __init__(self, api_key) -> None:
        self.sys_prompt = "What is in this image? Describe it to a person who is blind."
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro-vision")
        logger.info("ImgProc initialized")

    def raw(self, fp:str):
        img = Image.open(fp).convert("RGB")
        return ''.join(p.text for p in self.model.generate_content([self.sys_prompt, img]).candidates[0].content.parts)

    def consume(self, url: str):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert('RGB')
        a = ''.join(p.text for p in self.model.generate_content([self.sys_prompt, img]).candidates[0].content.parts);
        ocr_output = ocr_string(img); print("ocr_output: ", ocr_output);
        return f"##<img url='{url}'>##{a}##</img>## seemingly containing the text: \'{ocr_output}\'";


class YoutubeProcAction(abcs.MultimediaProc):
    def consume(self, url: str):
        # return "##<video>## Video is currently unavailable ##</video>##"
        stost = lambda s: f"{s//60:02}:{s%60:02}"
        a = "\n".join(
            f"{stost(i*5)}: {action}"
            for i, action in enumerate(infer.process_video(url))
        )
        return f"##<video url='{url}'>##{a}##</video>##";

class YoutubeProcKF(abcs.MultimediaProc):

    def __init__(self, key):
        self.key = key;

    def consume(self, url: str):
        chunk_dir = "output"
        impl.kf_proc.download_url(url)
        ip = ImgProc(key)
        ret = f"##<video url='{url}'##"
        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        #     futures = {}
        #     for i, kf in enumerate(os.listdir(chunk_dir)):
        #         if os.path.isfile(os.path.join(chunk_dir, kf)):
        #             futures[i] = executor.submit(ip.raw, f'{chunk_dir}/{kf}')
        #     results = {i: t.result() for i, t in futures.items()}
        # for i,_ in enumerate(os.listdir(chunk_dir)):
        #     ret += f'Keyframe {i}: {results[i]}'
        for i, kf in enumerate(os.listdir(chunk_dir)):
            if os.path.isfile(os.path.join(chunk_dir, kf)):
                ret += f'Keyframe {i}: {ip.raw(f"{chunk_dir}/{kf}")}'
                logger.info(f"Processed frame {i}")
        return ret+'##</video>##'

class WebpageProc(abcs.MultimediaProc):
    def consume(self, url: str):
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()
        logger.info("Website parsed")
        return f"##<article>##{text}##</article>";


class ProcMux(abcs.MultimediaProc):
    def __init__(self, key):
        self.api_key = key;

    """
    A processor that multiplexes other processors.
    """
    def consume(self, url: str):
        response = requests.head(url)
        if response.status_code != 200:
            logger.warn("Failed to load url. May have expired")
            return "##<generic>## The url failed to load ignore this and continue to look at chat##</generic>##"
        mime_type = response.headers.get("Content-Type")

        if mime_type.startswith("image/"):
            ip = ImgProc(self.api_key)
            return ip.consume(url)
        for l in re.findall(
            r"(?P<url>https?://www\.youtube\.com/watch\?v=[\w-]+)", url
        ):
            yp = YoutubeProcKF(self.api_key)
            return yp.consume(l)

        # Default proc is web-page proc.
        wp = WebpageProc()
        return wp.consume(url)
