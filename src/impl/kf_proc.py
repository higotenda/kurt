from pytube import YouTube
import subprocess
import os
import shutil

def download_url(url: str, chunk_dir="output") -> None:
    yt = YouTube(url)
    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).asc().first().download(filename="input.mp4")

    if os.path.exists(chunk_dir):
        shutil.rmtree(chunk_dir)
    os.makedirs(chunk_dir)

    input_file = "input.mp4"
    output_pattern = f"./{chunk_dir}/%d.jpg"

    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', "select='eq(pict_type\,I)',showinfo",
        '-vsync', 'vfr',
        output_pattern
    ]


    subprocess.run(command)

if __name__=='__main__':
    download_url("https://www.youtube.com/watch?v=jNQXAC9IVRw")