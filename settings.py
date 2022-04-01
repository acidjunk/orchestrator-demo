from pydantic import BaseSettings


class CompanySettings(BaseSettings):
    TRACING_ENABLED: bool = False
    SENTRY_DSN: str = ""
    TRACE_SAMPLE_RATE: float = 0.1


company_settings = CompanySettings()
