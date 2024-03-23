import google.generativeai as genai
import abcs
import os
import requests
from io import BytesIO
import re
import infer
from PIL import Image

class ImgProc(abcs.MultimediaProc):
    def __init__(self) -> None:
        self.ys_prompt = "What is in this image? Describe it to a person who is blind."
        genai.configure(api_key=os.environ["API_KEY"])
        self.model = genai.GenerativeModel("gemini-pro-vision")
    
    def consume(self, url: str):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        ''.join(p.text for p in response.candidates[0].content.parts)
        return f"##<img url='{url}'>##{''.join(p.text for p in self.model.generate_content([self.sys_prompt, img]).candidates[0].content.parts)}##</img>##"

class YoutubeProc(abcs.MultimediaProc):
    def consume(self, url: str):
        stost = lambda s: f"{s//60:02}:{s%60:02}"
        f"##<video url='{url}'>##{'\n'.join(f'{stost(i*5)}: {action}' for i,action in enumerate(infer.process_video(url)))}##</video>##"

class ProcMux(abcs.MultimediaProc):
    def consume(self, url: str):
        response = requests.head(url)
        mime_type = response.headers.get("Content-Type")

        if mime_type.startswith("image/"):
            return ImgProc.consume(url)
        for l in re.findall(r"(?P<url>https?://www\.youtube\.com/watch\?v=[\w-]+)", url):
            return YoutubeProc
        
        

        return 'A link to a webpage which is inaccessible'