from datetime import datetime,timezone

def today():
    return datetime.now(timezone.utc)


def make_epm_entry(
    luy_entry,
    list_type: str,
    category_reason: str,
    decision_date: bool = True
):
    return {
        "software_id": luy_entry["id"],
        "software_name": luy_entry["name"],
        "list_type": list_type,
        "entry_date": today(),
        "decision_date": today() if decision_date else None,
        "category_reason": category_reason,
        "policy": list_type
    }
