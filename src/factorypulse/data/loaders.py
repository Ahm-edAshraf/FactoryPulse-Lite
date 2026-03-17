"""Dataset loaders for CMAPSS and compatible sensor files."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd

from factorypulse.schemas import CMAPSS_COLUMNS


NASA_CMAPSS_URL = "https://data.nasa.gov/docs/legacy/CMAPSSData.zip"


def load_cmapss_split(file_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        engine="python",
    )

    if frame.shape[1] > len(CMAPSS_COLUMNS):
        frame = frame.iloc[:, : len(CMAPSS_COLUMNS)]

    frame.columns = CMAPSS_COLUMNS
    return frame


def load_rul_truth(file_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(file_path, sep=r"\s+", header=None, engine="python")
    if frame.shape[1] > 1:
        frame = frame.iloc[:, :1]
    frame.columns = ["rul"]
    return frame.reset_index(names="row_id")


def ensure_cmapss_files(data_dir: str | Path, subset_id: str = "FD001") -> dict[str, Path]:
    target_dir = Path(data_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "train": target_dir / f"train_{subset_id}.txt",
        "test": target_dir / f"test_{subset_id}.txt",
        "truth": target_dir / f"RUL_{subset_id}.txt",
    }
    if all(path.exists() for path in paths.values()):
        return paths

    zip_path = target_dir / "CMAPSSData.zip"
    if not zip_path.exists():
        urlretrieve(NASA_CMAPSS_URL, zip_path)

    with ZipFile(zip_path, "r") as archive:
        for member in archive.namelist():
            if member.endswith(f"train_{subset_id}.txt") or member.endswith(f"test_{subset_id}.txt") or member.endswith(f"RUL_{subset_id}.txt"):
                archive.extract(member, target_dir)
                extracted = target_dir / member
                extracted.replace(target_dir / Path(member).name)

    return paths
