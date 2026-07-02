import csv
from pathlib import Path

from scripts.prepare_dataset import build_manifest, build_manifest_from_dirs, write_manifest


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_build_manifest_pairs_visible_and_thermal_by_sequence(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "DJI_20260602140225_0400_T.JPG")

    rows = build_manifest(tmp_path)

    assert rows == [
        {
            "sequence_id": "0400",
            "visible_filename": "DJI_20260602140225_0400_V.JPG",
            "thermal_filename": "DJI_20260602140225_0400_T.JPG",
            "visible_exists": "yes",
            "thermal_exists": "yes",
            "notes": "",
        }
    ]


def test_build_manifest_reports_missing_pair(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "DJI_20260602140226_0401_T.JPG")

    rows = build_manifest(tmp_path)

    assert rows[0]["sequence_id"] == "0400"
    assert rows[0]["thermal_exists"] == "no"
    assert rows[0]["notes"] == "missing thermal"
    assert rows[1]["sequence_id"] == "0401"
    assert rows[1]["visible_exists"] == "no"
    assert rows[1]["notes"] == "missing visible"


def test_build_manifest_ignores_non_target_files(tmp_path):
    touch(tmp_path / "DJI_20260602140225_0400_V.JPG")
    touch(tmp_path / "notes.txt")
    touch(tmp_path / "preview.png")

    rows = build_manifest(tmp_path)

    assert len(rows) == 1
    assert rows[0]["sequence_id"] == "0400"


def test_build_manifest_from_separate_visible_and_thermal_dirs(tmp_path):
    visible_dir = tmp_path / "visible"
    thermal_dir = tmp_path / "thermal"
    touch(visible_dir / "DJI_20260602140225_0400_V.JPG")
    touch(thermal_dir / "DJI_20260602140225_0400_T.JPG")

    rows = build_manifest_from_dirs(visible_dir, thermal_dir)

    assert rows == [
        {
            "sequence_id": "0400",
            "visible_filename": "DJI_20260602140225_0400_V.JPG",
            "thermal_filename": "DJI_20260602140225_0400_T.JPG",
            "visible_exists": "yes",
            "thermal_exists": "yes",
            "notes": "",
        }
    ]


def test_write_manifest_outputs_csv(tmp_path):
    rows = [
        {
            "sequence_id": "0400",
            "visible_filename": "v.JPG",
            "thermal_filename": "t.JPG",
            "visible_exists": "yes",
            "thermal_exists": "yes",
            "notes": "",
        }
    ]
    output = tmp_path / "manifest.csv"

    write_manifest(rows, output)

    with output.open("r", encoding="utf-8", newline="") as handle:
        loaded = list(csv.DictReader(handle))
    assert loaded == rows
