from scarab.download import download_file
from pathlib import Path
import pytest
import os

os.chdir(Path(__file__).parent / "tmp")

@pytest.fixture
def url():
    return "https://arxiv.org/pdf/2410.18119"

def test_download_file(url):
    download_file(url, "test.pdf", fix_extension=False)
    download_file(url, "test.png", fix_extension=True)
    download_file(url, fix_extension=True)
    # Remove all pdf files
    for file in Path(".").rglob("*.pdf"):
        file.unlink()

