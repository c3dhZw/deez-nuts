import enum


class Rating(enum.Enum):
    """Enum for e621 rating."""

    NONE = None
    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"
