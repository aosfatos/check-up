from dataclasses import dataclass
from typing import List


@dataclass
class AdItem:
    title: str
    url: str
    thumbnail_url: str | None = None
    tag: str | None = None
    screenshot_path: str | None = None
    excerpt: str | None = None

    def is_valid(self):
        if self.url is None or self.title is None:
            return False
        return True

    def __str__(self):
        url = self.url[:50] if self.url else None
        return f"{self.title}: ({url})"


@dataclass
class EntryItem:
    title: str
    url: str
    ads: List[AdItem]
    screenshot_path: str | None = None

    def __str__(self):
        return f"{self.title}: ({self.url[:50]})"
