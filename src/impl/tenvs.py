from abcs import TextEnv, Link, regex_url
from typing import Iterator, Iterable

class ListEnv(TextEnv):
    """
    A TextEnv implementor, that regex searches iterable for links element-wise.
    """
    def __init__(self, ls: list[str]):
        self.iters = ls;
        
    def hist(self):
        links = [];
        for line in self.iters:
            links.extend(regex_url(line));
        return (self.iters, links);

class LinesEnv(TextEnv):
    """
    A TextEnv implementor, that maintains a history of lines pushed, and a list of links contained within them.
    """
    def __init__(self, reverse=False):
        self.texts: list[str] = [];
        self.links: list[Link] = [];
        self.reverse: bool = reverse;

    def pushline(self, line: str) -> None:
        """
        Insert this line into current text-env history.
        Also find all associated links.
        """
        self.texts.append(line);
        self.links.extend(regex_url(line));

    def hist(self):
        if self.reverse:
            self.texts.reverse();
            self.links.reverse();
        return (self.texts, self.links);