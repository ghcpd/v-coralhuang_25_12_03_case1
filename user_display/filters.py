"""Filter strategies for user records.

Provide a small, extensible framework of filters.
"""
from typing import Dict, Any


class BaseFilter:
    def match(self, user: Dict[str, Any]) -> bool:
        raise NotImplementedError()


class CriteriaFilter(BaseFilter):
    """Simple dict-driven filter with case sensitivity control.

    Accepts criteria like {'role': 'User', 'status': 'Active', 'name': 'john'}
    where name/email are substring matches by default.
    """

    def __init__(self, criteria: Dict[str, Any], case_sensitive: bool = False):
        self.criteria = criteria or {}
        self.case_sensitive = case_sensitive

    def _cmp(self, hay: str, needle: str) -> bool:
        if hay is None:
            return False
        if self.case_sensitive:
            return needle in hay
        return needle.lower() in hay.lower()

    def match(self, user: Dict[str, Any]) -> bool:
        for key, value in self.criteria.items():
            if key in ("name", "email"):
                if not self._cmp(user.get(key, ""), str(value)):
                    return False
            else:
                # exact match
                if user.get(key) != value:
                    return False

        return True
