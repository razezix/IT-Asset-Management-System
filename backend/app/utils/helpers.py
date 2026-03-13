import uuid


def generate_passport_uid() -> str:
    return f"PP-{uuid.uuid4().hex[:8].upper()}"


def compute_changed_fields(old: dict, new: dict) -> list[str]:
    """Return list of keys where values differ between old and new dicts."""
    return [k for k in new if old.get(k) != new.get(k)]
