import enum


class Rating(enum.Enum):
    """Enum for e621 rating."""

    SAFE = "s"
    QUESTIONABLE = "q"
    EXPLICIT = "e"
