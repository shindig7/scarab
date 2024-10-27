import requests
import filetype
import pathlib
from loguru import logger
from uuid import uuid4
import os
import datetime


def download_file(url: str, filename: str | None = None, fix_extension: bool = True, set_modification_date: bool = True) -> None:
    """ Download a file from a URL and save it to a file.

    Args:
        url (str): The URL to download the file from.
        filename (str): The name of the file to save the downloaded file to.
        fix_extension (bool): Whether to fix the file extension using the
            `filetype` library. Defaults to True.
    
    Returns:
        None
    """
    if not filename:
        filename = f"{uuid4()}"
        fix_extension = True
    try:
        filename = pathlib.Path(filename)
        with requests.get(url, stream=True) as r:
            with open(filename, "wb") as F:
                for chunk in r.iter_content(chunk_size=10 * 1024 * 1024):
                    F.write(chunk)

        if fix_extension:
            logger.debug(f"Fixing file extension for {filename}")
            kind = filetype.guess(filename)
            logger.debug(f"Detected file type: {kind}")
            if (kind is not None) and (kind.extension != filename.suffix[1:]):
                extension = kind.extension
                # Rename file with new extension using pathlib
                new_filename = pathlib.Path(filename).with_suffix(f".{extension}")
                pathlib.Path(filename).replace(new_filename)
                logger.debug(f"Renamed file to {new_filename}") 

        if set_modification_date:
            final_filename = new_filename or filename
            logger.debug(f"Setting modification date for {final_filename}")
            epoch = datetime.datetime.now().timestamp()
            os.utime(final_filename, (epoch, epoch))

    except Exception as e:
        logger.error(f"Failed to download file from {url}")
        logger.error(e)
    
if __name__ == "__main__":
    download_file("https://arxiv.org/pdf/2410.18119")
