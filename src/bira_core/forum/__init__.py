"""Forum topic routing facade."""

from bira_core.forum.service import (
    TOPIC_GONE_MARKERS,
    ForumTopics,
    ThreadStore,
)

__all__ = ["TOPIC_GONE_MARKERS", "ForumTopics", "ThreadStore"]
