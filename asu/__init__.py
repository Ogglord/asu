import os

# __version__ is surfaced on the landing page. Prefer a build-time /
# deploy-time override (e.g. a git short sha injected via the ASU_VERSION
# env var in the Containerfile or compose) and fall back to the literal
# below so local uv-run invocations still import cleanly.
__version__ = os.environ.get("ASU_VERSION") or "0.0.0"

# Optional deployment label shown alongside the version (e.g. "dev",
# "prod"). Empty string means "don't render the label" in templates.
__env__ = os.environ.get("ASU_ENV") or ""
