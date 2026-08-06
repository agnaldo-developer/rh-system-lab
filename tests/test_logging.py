import json
import logging

from app.core.logging_config import JsonFormatter


def test_json_formatter_includes_context() -> None:
    record = logging.LogRecord(
        name="rh_system.request",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Request completed",
        args=(),
        exc_info=None,
    )

    record.request_id = "teste-123"
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 12.5

    formatter = JsonFormatter()
    output = formatter.format(record)
    log_data = json.loads(output)

    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Request completed"
    assert log_data["request_id"] == "teste-123"
    assert log_data["method"] == "GET"
    assert log_data["path"] == "/health"
    assert log_data["status_code"] == 200
    assert log_data["duration_ms"] == 12.5
    assert "timestamp" in log_data
