from pytube import YouTube
import subprocess
import os


def download_url(url: str) -> None:
    yt = YouTube(url)
    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).asc().first().download(filename="input.mp4")

    if not os.path.exists("output"):
        os.makedirs("output")

    input_file = "input.mp4"
    output_pattern = "./output/%d.mp4"

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-c",
        "copy",
        "-map",
        "0",
        "-segment_time",
        "5",
        "-f",
        "segment",
        output_pattern,
    ]

    subprocess.run(command)


def demo():
    download_url("http://youtube.com/watch?v=9bZkp7q19f0")


if __name__ == "__main__":
    demo()
