"""
A module to contain processor multiplexers.
"""

import abcs
from procs.img_proc import ImgProc
from procs.kf_proc import YoutubeProcKF
from procs.web_proc import WebpageProc, head_content_type

# Introducing name change to make way for `GeneralMux`
class LProcMux(abcs.MultimediaProc):
    def __init__(self, key):
        self.api_key = key

    """
    A processor that multiplexes other processors.
    """

    def consume(self, url: str, mime_type=None) -> abcs.Serialized | None:
        # If Mime-Type was not provided, resolve it.
        if mime_type is None:
            mime_type = head_content_type(url)
            # If it is still none, you are unable to resolve resource. Return.
            if mime_type is None:
                return abcs.Serialized(
                    "##<generic>## The url failed to load ignore this and continue to look at chat##</generic>##"
                    );

        if (ret := ImgProc(self.api_key).consume(url, mime_type)):
            return ret;
        elif (ret := YoutubeProcKF(self.api_key).consume(url, mime_type)):
            return ret
        else:
            # Default proc is web-page proc.
            return WebpageProc().consume(url, mime_type);