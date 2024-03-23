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
from PIL import Image


class ImgProc(abcs.MultimediaProc):
    """
    Processor for image-type multi-media.
    """

    def __init__(self) -> None:
        self.sys_prompt = "What is in this image? Describe it to a person who is blind."
        genai.configure(api_key=os.environ["API_KEY"])
        self.model = genai.GenerativeModel("gemini-pro-vision")

    def consume(self, url: str):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return f"##<img url='{url}'>##{''.join(p.text for p in self.model.generate_content([self.sys_prompt, img]).candidates[0].content.parts)}##</img>##"


class YoutubeProc(abcs.MultimediaProc):
    def consume(self, url: str):
        # return "##<video>## Video is currently unavailable ##</video>##"
        stost = lambda s: f"{s//60:02}:{s%60:02}"
        a = "\n".join(
            f"{stost(i*5)}: {action}"
            for i, action in enumerate(infer.process_video(url))
        )
        f"##<video url='{url}'>##{a}##</video>##"


class WebpageProc(abcs.MultimediaProc):
    def consume(self, url: str):
        # return "##<article>## Articles are currently unvailable ##</article>##"
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()
        print(text)
        f"##<article>##{text}##</article>"


class ProcMux(abcs.MultimediaProc):
    """
    A processor that multiplexes other processors.
    """

    def consume(self, url: str):
        response = requests.head(url)
        if response.status_code != 200:
            return "##<generic>## The url failed to load ignore this and continue to look at chat##</generic>##"
        mime_type = response.headers.get("Content-Type")

        if mime_type.startswith("image/"):
            print("found image")
            ip = ImgProc()
            return ip.consume(url)
        for l in re.findall(
            r"(?P<url>https?://www\.youtube\.com/watch\?v=[\w-]+)", url
        ):
            yp = YoutubeProc()
            return yp.consume(l)

        # Default proc is web-page proc.
        wp = WebpageProc()
        return wp.consume(url)
