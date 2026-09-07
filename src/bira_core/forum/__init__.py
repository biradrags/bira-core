"""Forum topic routing facade."""

from bira_core.forum.service import (
    TOPIC_GONE_MARKERS,
    ForumTopics,
    ThreadStore,
    is_topic_gone,
)

__all__ = ["TOPIC_GONE_MARKERS", "ForumTopics", "ThreadStore", "is_topic_gone"]
