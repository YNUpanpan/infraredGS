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


def scan_images_by_kind(root: Path, expected_kind: str) -> dict[str, dict[str, str]]:
    expected_kind = expected_kind.upper()
    pairs: dict[str, dict[str, str]] = {}
    for path in sorted(root.iterdir()):
        if not path.is_file():
            continue
        match = IMAGE_PATTERN.search(path.name)
        if match is None or match.group("kind").upper() != expected_kind:
            continue
        sequence = match.group("sequence")
        pairs.setdefault(sequence, {})
        if expected_kind == "V":
            pairs[sequence]["visible"] = path.name
        elif expected_kind == "T":
            pairs[sequence]["thermal"] = path.name
    return pairs


def rows_from_pairs(pairs: dict[str, dict[str, str]]) -> list[dict[str, str]]:
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


def build_manifest(root: Path) -> list[dict[str, str]]:
    return rows_from_pairs(scan_images(root))


def build_manifest_from_dirs(visible_root: Path, thermal_root: Path) -> list[dict[str, str]]:
    pairs = scan_images_by_kind(visible_root, "V")
    thermal_pairs = scan_images_by_kind(thermal_root, "T")
    for sequence, values in thermal_pairs.items():
        pairs.setdefault(sequence, {}).update(values)
    return rows_from_pairs(pairs)


def write_manifest(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成可见光/红外无人机图像 manifest。")
    parser.add_argument("--input", type=Path, default=Path("."), help="原始图片所在目录")
    parser.add_argument("--visible-dir", type=Path, help="可见光图片目录")
    parser.add_argument("--thermal-dir", type=Path, help="红外图片目录")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("manifests/dataset_manifest.csv"),
        help="输出 CSV 路径",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.visible_dir or args.thermal_dir:
        if not args.visible_dir or not args.thermal_dir:
            raise SystemExit("--visible-dir 和 --thermal-dir 必须同时提供。")
        rows = build_manifest_from_dirs(args.visible_dir, args.thermal_dir)
    else:
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
