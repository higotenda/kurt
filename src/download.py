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
    output_pattern = f"./{chunk_dir}/%d.mp4"

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-c",
        "copy",
        "-map",
        "0",
        "-f",
        "segment",
        "-segment_time",
        "5",
        "-reset_timestamps",
        "1",
        output_pattern,
    ]

    subprocess.run(command)


if __name__ == "__main__":
    download_url("http://youtube.com/watch?v=9bZkp7q19f0")