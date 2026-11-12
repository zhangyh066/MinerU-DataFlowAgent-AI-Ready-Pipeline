"""RAG 调用链观测：本地 JSONL 审计 + 可选 OTLP（Phoenix/Langfuse 兼容后端）。"""

import json
import logging
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


class RAGTrace:
    def __init__(self, manager, trace_id, question, metadata):
        self.manager = manager
        self.trace_id = trace_id
        self.record = {
            "trace_id": trace_id,
            "question": question,
            "started_at": _utc_now(),
            "metadata": metadata,
            "events": [],
        }
        self.span = None

    def event(self, name, **attributes):
        attributes = {key: value for key, value in attributes.items() if value is not None}
        payload = {"name": name, "time": _utc_now(), **attributes}
        self.record["events"].append(payload)
        if self.span is not None:
            self.span.add_event(name, attributes=attributes)

    def finish(self, status="ok", error=None):
        self.record["status"] = status
        self.record["finished_at"] = _utc_now()
        if error is not None:
            self.record["error"] = str(error)
        self.manager._write(self.record)
        if self.span is not None:
            if error is not None:
                self.span.record_exception(error)
            self.span.end()


class RAGObservability:
    def __init__(self, log_dir=None, enabled=None, otlp_endpoint=None):
        self.enabled = self._env_bool("RAG_OBSERVE_ENABLED", False) if enabled is None else enabled
        default_dir = Path(__file__).resolve().parent.parent / "logs"
        self.log_dir = Path(log_dir or os.getenv("RAG_OBSERVE_DIR", default_dir))
        self.otlp_endpoint = otlp_endpoint or os.getenv("RAG_OTLP_ENDPOINT")
        self.provider = None
        self.tracer = None
        if self.enabled:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            if self.otlp_endpoint:
                self._setup_otlp()

    @staticmethod
    def _env_bool(name, default):
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    def _setup_otlp(self):
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            provider = TracerProvider(resource=Resource.create({"service.name": "mineru-rag"}))
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=self.otlp_endpoint)))
            self.provider = provider
            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer("mineru.rag")
        except Exception as exc:
            log.warning("OTLP 初始化失败，将仅使用 JSONL：%s", exc)
            self.tracer = None

    @contextmanager
    def trace(self, question, **metadata):
        trace_id = uuid.uuid4().hex
        if not self.enabled:
            yield RAGTrace(self, trace_id, question, metadata)
            return

        record = RAGTrace(self, trace_id, question, metadata)
        if self.tracer is not None:
            record.span = self.tracer.start_span(
                "rag.ask",
                attributes={"rag.question": question, **{
                    key: str(value) for key, value in metadata.items()
                }},
            )
        try:
            yield record
        except Exception as exc:
            record.finish(status="error", error=exc)
            raise
        else:
            record.finish()

    def _write(self, record):
        if not self.enabled:
            return
        path = self.log_dir / "rag_traces.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def feedback(self, trace_id, rating, error_type="", comment=""):
        if not self.enabled:
            raise RuntimeError("观测未开启，无法记录反馈")
        feedback_id = uuid.uuid4().hex
        payload = {
            "feedback_id": feedback_id,
            "trace_id": trace_id,
            "rating": rating,
            "error_type": error_type,
            "comment": comment,
            "time": _utc_now(),
        }
        path = self.log_dir / "feedback.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        if self.tracer is not None:
            with self.tracer.start_as_current_span("rag.feedback") as span:
                span.set_attribute("rag.trace_id", trace_id)
                span.set_attribute("rag.rating", rating)
                span.set_attribute("rag.error_type", error_type)
        return feedback_id

    def shutdown(self):
        if self.provider is not None:
            self.provider.shutdown()
