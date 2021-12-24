from api_types import Record, FieldMetadata


FIELDS_TO_SKIP = {"date"}


def diff_classname_filter(
    current_record: Record, previous_record: Record, field: FieldMetadata
) -> str:
    field_name = field["FieldName"]
    if field_name in FIELDS_TO_SKIP:
        return ""

    if not previous_record:
        return ""

    if previous_record.get(field_name) != current_record.get(field_name):
        return "has_diff"

    return ""


def diff_record_filter(current_record: dict, previous_record: dict) -> bool:
    if not previous_record:
        return False
    # Override date keys so they're the same for all comparisons
    return {**current_record, "date": True} == {**previous_record, "date": True}
