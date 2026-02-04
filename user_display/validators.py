from typing import Tuple, Optional, Iterable


# Returns (valid: bool, error_message: Optional[str])
def default_validate_user(
    user: dict,
    required_id: bool = True,
    required_fields: Optional[Iterable[str]] = None,
) -> Tuple[bool, Optional[str]]:
    if not isinstance(user, dict):
        return False, "User record is not a dict"

    if required_id and "id" not in user:
        return False, "User missing required 'id' field"

    if required_fields:
        for field in required_fields:
            if field not in user:
                return False, f"User id={user.get('id', 'N/A')} missing required field '{field}'"

    return True, None
