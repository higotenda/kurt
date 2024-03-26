from abc import ABC, abstractmethod
from typing import NewType, Optional
import re
import logging

logger = logging.getLogger(__name__)

Link = NewType("Link", str)
Serialized = NewType("Serialized", str)
# For now. SafeTensor.


URL_REGEX = re.compile(r"(https?://[^\s]+)");

class TextEnv(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def hist(self, *kwargs) -> tuple[list[str], list[Link]]:
        """Return a history of everything that's transpired in the chat. Kwargs can be used to supply additional arguments."""
        pass


class DataProvider(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch(self, media_id: str) -> Serialized | None:
        """Check if required resource already is cached in the database."""
        pass

    @abstractmethod
    def write(self, media_id: str, data: Serialized) -> bool:
        """Cache serialized data, and return true if successful."""
        pass

    @abstractmethod
    def terminate(self):
        """Close data provider safely."""
        pass


class MultimediaProc(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def consume(self, url: str, mime_type: Optional[str]=None) -> Optional[Serialized]:
        """
        Fetch multimedia from url, process and return serialized data.
        If provided mime_type is incompatiable with the processor, return None.
        If mime_type is None, processor is expected to resolve it via head requests.
        """
        pass


class LLMActor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_base(self, text_data, ser_data) -> str:
        """Get rich summarization from lllm."""
        pass

    @abstractmethod
    def send_prompt(self, prompt) -> str:
        """Get prompt results."""
        pass

    @abstractmethod
    def clean(self) -> None:
        """Clear Context"""
        pass


def regex_url(search_str: str) -> list[Link]:
    """Search input string for links."""
    return URL_REGEX.findall(search_str);


def kurt_eat(
    env: TextEnv, prov: DataProvider, proc: MultimediaProc, actor: LLMActor
) -> str:
    actor.clean()
    text, links = env.hist()
    processed = []
    for link in links:
        logger.info("Checking Provider for link..");
        ret = prov.fetch(link)
        if ret is None:
            logger.info("Link not found in provider, will consume..");
            
            ret = proc.consume(link)
            if ret is None:
                logger.warn(f"Top-level processor did not consume link {link}.");
                continue;
            elif ret == "":
                logger.warn(f"Processor returned empty for link {link}")

            logger.info(f"Attempting to cache processed data for {link}");

            try:
                if not prov.write(link, ret):
                    logger.warn(f"Failed to cache result for link {link}, but did not error.")
            except Exception as e:
                logger.error("Data Provider has failed.\n\tcause: " + str(e));
            
            processed.append(ret)

    logger.info("Sending base data to actor..");
    return actor.send_base(text, processed)


def kurt_interrogate(question: str, actor: LLMActor) -> str:
    return actor.send_prompt(question)
