from dataclasses import dataclass
from typing import List


@dataclass
class AdItem:
    title: str
    url: str
    thumbnail_url: str
    tag: str | None = None
    screenshot_path: str | None = None
    excerpt: str | None = None

    def __str__(self):
        return f"{self.title}: ({self.url[:50]})"


@dataclass
class EntryItem:
    title: str
    url: str
    ads: List[AdItem]
    screenshot_path: str | None = None

    def __str__(self):
        return f"{self.title}: ({self.url[:50]})"
