from pathlib import Path
import re
import urllib3


def generic_request(url: str, directory: str | None) -> str | None:
    try:
        req: urllib3.BaseHTTPResponse = urllib3.request(
            "GET", url, headers={"User-Agent": "Chrome/120.0.0.0"})

        if req.status != 200:
            raise IOError(f"HTTP Error: {req.status}")

        if directory:
            filename: str = url.split("/")[-1]
            file_path: Path = Path(directory) / filename

            file_path.write_bytes(req.data)
            return str(file_path)
        else:
            return req.data.decode("utf-8")
    except Exception:
        raise IOError


def get_tags() -> list[str] | None:
    try:
        tags_list = generic_request(
            "https://github.com/crosire/reshade/tags", None)

        if not tags_list:
            return None

        return re.findall(r"(?<=releases/tag/v)[0-9.]+", tags_list)
    except Exception:
        raise IOError


# generic_request("https://github.com/crosire/reshade/tags", None)
# generic_request("https://reshade.me/downloads/ReShade_Setup_6.7.1.exe",
#                  QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation))
# print(get_tags())
