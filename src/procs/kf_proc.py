"""
A module implementing KeyFrames-based processor for 
"""


import logging
from pytube import YouTube
import subprocess
import os
import shutil
import re
import abcs
from procs.img_proc import ImgProc

YOUTUBE_WATCH_URL_REGEX = re.compile(r"(?P<url>https?://www\.youtube\.com/watch\?v=[\w-]+)");
logger = logging.getLogger(__name__);

class YoutubeProcKF(abcs.MultimediaProc):
    """
    A Processor to download a youtube video, extract its keyframes and feed it to the image processor.
    """

    def __init__(self, key):
        self.key = key

    def consume(self, url: str, mime_type=None):
        match = YOUTUBE_WATCH_URL_REGEX.search(url);
        if match is None:
            return None;

        chunk_dir = "output"
        download_url(url)

        ip = ImgProc(self.key)
        ret = f"##<video url='{url}'##"

        for i, kf in enumerate(os.listdir(chunk_dir)):
            if os.path.isfile(os.path.join(chunk_dir, kf)):
                ret += f'Keyframe {i}: {ip.raw(f"{chunk_dir}/{kf}")}'
                logger.info(f"Processed frame {i}")

        return abcs.Serialized(ret + "##</video>##");

def download_url(url: str, chunk_dir="output") -> None:
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).asc().first();
    if stream is None:
        logger.error(f"YouTube url {url} does not resolve to any streams.");
        return None;

    input_file = "input.mp4"
    stream.download(filename=input_file);

    if os.path.exists(chunk_dir):
        shutil.rmtree(chunk_dir)
    os.makedirs(chunk_dir)
    output_pattern = f"./{chunk_dir}/%d.jpg"

    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', r"select='eq(pict_type\,I)',showinfo",
        '-vsync', 'vfr',
        output_pattern
    ]
    subprocess.run(command)