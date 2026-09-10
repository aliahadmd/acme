"""Export the OpenAPI schema for the generated TS client.

Run by the turbo `schema` task (`make client`). Writes to
packages/api-client/openapi.json, which is committed so agents and reviewers
can see the API contract in PR diffs.
"""

import json
import os
import pathlib
import sys

os.environ.setdefault("DATABASE_URL", "sqlite://")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # flat layout: add app root

from app.main import app  # noqa: E402  (must import after env/path are configured)

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "packages" / "api-client" / "openapi.json"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(app.openapi(), indent=2) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
