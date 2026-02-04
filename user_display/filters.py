from abc import ABC, abstractmethod


class FilterStrategy(ABC):
    @abstractmethod
    def matches(self, user: dict) -> bool:
        pass


class RoleFilter(FilterStrategy):
    def __init__(self, role):
        self.role = role

    def matches(self, user: dict) -> bool:
        return user.get("role") == self.role


class StatusFilter(FilterStrategy):
    def __init__(self, status):
        self.status = status

    def matches(self, user: dict) -> bool:
        return user.get("status") == self.status


class NameContainsFilter(FilterStrategy):
    def __init__(self, substring, case_sensitive=False):
        self.substring = substring
        self.case_sensitive = case_sensitive

    def matches(self, user: dict) -> bool:
        name = user.get("name", "")
        if not self.case_sensitive:
            return self.substring.lower() in name.lower()
        return self.substring in name


class EmailContainsFilter(FilterStrategy):
    def __init__(self, substring, case_sensitive=False):
        self.substring = substring
        self.case_sensitive = case_sensitive

    def matches(self, user: dict) -> bool:
        email = user.get("email", "")
        if not self.case_sensitive:
            return self.substring.lower() in email.lower()
        return self.substring in email


class CompositeFilter(FilterStrategy):
    def __init__(self, strategies):
        self.strategies = strategies

    def matches(self, user: dict) -> bool:
        return all(s.matches(user) for s in self.strategies)
