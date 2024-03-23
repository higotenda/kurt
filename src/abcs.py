from abc import ABC
from typing import NewType, abstractmethod
import re

Link = NewType("Link", str)
JsonData = NewType("JsonData", str)
Serialized = JsonData
# For now. SafeTensor.


class TextEnv(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def hist(*kwargs) -> tuple[list[str], list[Link]]:
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
    def consume(self, url: str) -> Serialized:
        """Fetch multimedia from url, process and return serialized data."""
        pass


class LLMActor(ABC):
    def __init__(self):
        pass

    def send_base(self, text_data, ser_data) -> str:
        """Get rich summarization from lllm."""
        pass

    def send_prompt(self, prompt) -> str:
        """Get prompt results."""
        pass

    def clean(self) -> None:
        """Clear Context"""
        pass


def regex_url(search_str: str) -> list[Link]:
    """Search input string for links."""
    return re.findall(r"(https?://[^\s]+)", search_str)


def kurt_eat(
    env: TextEnv, prov: DataProvider, proc: MultimediaProc, actor: LLMActor
) -> str:
    actor.clean()
    text, links = env.hist()
    mm_data = []
    for link in links:
        ret = None
        try:
            ret = prov.fetch(link)
        except:
            print("Mongo is dead")
        if ret is None:
            ret = proc.consume(link)
            try:
                if not prov.write(link, ret):
                    print(f"Warning: Failed to cache result for link {link}")
            except:
                print("Mongo is dead")
        mm_data.append(ret)
        mm_data = list(filter(lambda x: x is not None, mm_data))
    return actor.send_base(text, mm_data)


def kurt_interrogate(question: str, actor: LLMActor) -> str:
    return actor.send_prompt(question)
