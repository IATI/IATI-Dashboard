"""Per-dataset-historic-event rendering for DatasetHistoricEvent rows.

Handlers are registered against a `(message_type, display_category)` pair —
where `display_category=None` means "match any display_category for this
message_type". Lookup tries the specific pair first and falls back to the
bare-message_type entry, so a handler registered without a display_category
acts as the default for all rows of that type.

Each handler supplies a template path and a function that maps the raw
payload dict to a presentation context dict. `render_message_type_for_payload`
returns `{"template": ..., "context": ...}` so the templates can
`{% include ITEM.template %}` and reference `ITEM.context.*` (dataset.html
calls the dataset history event dataset_change_event).
"""

from dataclasses import dataclass
from typing import Any, Callable

PayloadHandler = Callable[[dict], dict]


@dataclass(frozen=True)
class FieldComparisonSpec:
    label: str
    path: str  # dotted, e.g. "last_known_good_dataset.hash"


@dataclass(frozen=True)
class DatasetHistoricEventHandler:
    template: str
    handler: PayloadHandler


REGISTRY: dict[tuple[str, str | None], DatasetHistoricEventHandler] = {}


def register(
    message_type: str,
    template: str,
    display_category: str | None = None,
) -> Callable[[PayloadHandler], PayloadHandler]:
    def decorator(fn: PayloadHandler) -> PayloadHandler:
        REGISTRY[(message_type, display_category)] = DatasetHistoricEventHandler(
            template=f"_partials/activity_stream/{template}", handler=fn
        )
        return fn

    return decorator


def message_type_has_handler(
    message_type: str,
    display_category: str | None,
) -> bool:
    return (message_type, display_category) in REGISTRY or (message_type, None) in REGISTRY


def render_message_type_for_payload(
    message_type: str,
    display_category: str | None,
    payload: dict | None,
) -> dict:
    handler = REGISTRY.get((message_type, display_category)) or REGISTRY.get((message_type, None))
    if handler is None:
        return {"template": None, "context": {}}
    return {"template": handler.template, "context": handler.handler(payload or {})}


def get_field_value_from_path(d: Any, path: str) -> Any:
    for key in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d


def diff_fields(
    previous: dict | None,
    current: dict | None,
    fields: list[FieldComparisonSpec],
) -> list[tuple[str, Any, Any]]:
    """Return (label, old, new) for each field whose value differs."""
    rows: list[tuple[str, Any, Any]] = []
    for field_spec in fields:
        old = get_field_value_from_path(previous, field_spec.path)
        new = get_field_value_from_path(current, field_spec.path)
        if old != new:
            rows.append((field_spec.label, old, new))
    return rows


@register(
    "DATASET_CREATED",
    "dataset_created.html",
)
def dataset_metadata_any_change(payload: dict) -> dict[str, Any]:
    updated_fields = diff_fields(
        payload.get("dataset_previous"),
        payload.get("dataset"),
        [
            FieldComparisonSpec("Short name", "short_name"),
            FieldComparisonSpec("Source type", "source_type"),
            FieldComparisonSpec("URL", "url"),
            FieldComparisonSpec("Licence ID", "licence_id"),
            FieldComparisonSpec("Visibility", "visibility"),
        ],
    )
    return {"label": "Dataset created", "updated_fields": updated_fields}


@register(
    "DATASET_UPDATED",
    "dataset_field_diff_view.html",
)
def dataset_metadata_updated(payload: dict) -> dict[str, Any]:
    updated_fields = diff_fields(
        payload.get("dataset_previous", {}),
        payload.get("dataset"),
        [
            FieldComparisonSpec("Short name", "short_name"),
            FieldComparisonSpec("Source type", "source_type"),
            FieldComparisonSpec("URL", "url"),
            FieldComparisonSpec("Licence ID", "licence_id"),
            FieldComparisonSpec("Visibility", "visibility"),
        ],
    )
    return {"label": "Metadata updated", "updated_fields": updated_fields}


@register(
    "DATASET_CHECK_RESULT",
    "dataset_field_diff_view.html",
    display_category="CONTENT_CHANGED_EXCLUDING_GENERATED_TIMESTAMP",
)
def dataset_check_result_content_changed(payload: dict) -> dict[str, Any]:
    updated_fields = diff_fields(
        payload.get("dataset_check_result_previous"),
        payload.get("dataset_check_result"),
        [
            FieldComparisonSpec("Hash", "last_known_good_dataset.hash_excluding_generated_timestamp"),
            FieldComparisonSpec("Content length", "last_known_good_dataset.content_length"),
        ],
    )
    return {"label": "Contents of dataset changed", "updated_fields": updated_fields}


@register(
    "DATASET_CHECK_RESULT",
    "dataset_field_diff_view.html",
    display_category="DOWNLOAD_STATUS_CHANGED",
)
def dataset_check_result_download_status_changed(payload: dict) -> dict[str, Any]:
    updated_fields = diff_fields(
        payload.get("dataset_check_result_previous"),
        payload.get("dataset_check_result"),
        [
            FieldComparisonSpec("HTTP Status", "most_recent_get_attempt.http_status"),
            FieldComparisonSpec("Error occurred", "most_recent_get_attempt.error_occurred"),
            FieldComparisonSpec("Error details", "most_recent_get_attempt.error_details.error_type"),
        ],
    )
    return {"label": "Download status changed", "updated_fields": updated_fields}
