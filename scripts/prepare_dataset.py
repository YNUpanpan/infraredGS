from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = [
    "sequence_id",
    "visible_filename",
    "thermal_filename",
    "visible_exists",
    "thermal_exists",
    "notes",
]

IMAGE_PATTERN = re.compile(r"_(?P<sequence>\d{4})_(?P<kind>[VT])\.JPG$", re.IGNORECASE)


def scan_images(root: Path) -> dict[str, dict[str, str]]:
    pairs: dict[str, dict[str, str]] = {}
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        match = IMAGE_PATTERN.search(path.name)
        if match is None:
            continue
        sequence = match.group("sequence")
        kind = match.group("kind").upper()
        pairs.setdefault(sequence, {})
        if kind == "V":
            pairs[sequence]["visible"] = path.name
        elif kind == "T":
            pairs[sequence]["thermal"] = path.name
    return pairs


def build_manifest(root: Path) -> list[dict[str, str]]:
    pairs = scan_images(root)
    rows: list[dict[str, str]] = []
    for sequence in sorted(pairs):
        visible = pairs[sequence].get("visible", "")
        thermal = pairs[sequence].get("thermal", "")
        notes = ""
        if not visible:
            notes = "missing visible"
        elif not thermal:
            notes = "missing thermal"
        rows.append(
            {
                "sequence_id": sequence,
                "visible_filename": visible,
                "thermal_filename": thermal,
                "visible_exists": "yes" if visible else "no",
                "thermal_exists": "yes" if thermal else "no",
                "notes": notes,
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成可见光/红外无人机图像 manifest。")
    parser.add_argument("--input", type=Path, default=Path("."), help="原始图片所在目录")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("manifests/dataset_manifest.csv"),
        help="输出 CSV 路径",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_manifest(args.input)
    write_manifest(rows, args.output)
    complete = sum(
        1
        for row in rows
        if row["visible_exists"] == "yes" and row["thermal_exists"] == "yes"
    )
    print(f"manifest rows: {len(rows)}")
    print(f"complete pairs: {complete}")
    print(f"output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
