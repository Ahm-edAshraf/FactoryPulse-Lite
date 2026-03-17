from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_factorypulse_package_imports() -> None:
    import factorypulse

    assert hasattr(factorypulse, "__version__")
