import io
import json
import os
import zipfile
from typing import Tuple, Dict, Any

from django.conf import settings


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def extract_h5p_archive(file_bytes: bytes, destination_dir: str) -> None:
    """Extract a .h5p (zip) archive into destination_dir."""
    ensure_directory(destination_dir)
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        zf.extractall(destination_dir)


def load_h5p_json(extracted_root: str) -> Dict[str, Any]:
    """Load and return the parsed h5p.json from an extracted package."""
    h5p_json_path = os.path.join(extracted_root, "h5p.json")
    with open(h5p_json_path, "r", encoding="utf-8") as fp:
        return json.load(fp)


def derive_library_from_h5p_json(h5p_json: Dict[str, Any]) -> Tuple[str, int, int, int]:
    """Return (name, major, minor, patch) for the package's main library.

    Falls back to (0,0,0) if version is not found.
    """
    main_library = h5p_json.get("mainLibrary")
    version_major = 0
    version_minor = 0
    version_patch = 0
    for dep in h5p_json.get("preloadedDependencies", []):
        if dep.get("machineName") == main_library:
            version_major = int(dep.get("majorVersion", 0))
            version_minor = int(dep.get("minorVersion", 0))
            version_patch = int(dep.get("patchVersion", 0))
            break
    return main_library or "Unknown", version_major, version_minor, version_patch


def get_content_storage_dir(content_id: int) -> str:
    """Absolute path for extracted files of a content item."""
    base = settings.MEDIA_ROOT
    return os.path.join(base, "h5p", "content", str(content_id))


def safe_path_join(root: str, relative_path: str) -> str:
    """Safely join a user-supplied relative path under root, preventing traversal."""
    normalized = os.path.normpath(relative_path).lstrip(os.sep)
    full_path = os.path.normpath(os.path.join(root, normalized))
    if not full_path.startswith(os.path.normpath(root) + os.sep) and full_path != os.path.normpath(root):
        raise ValueError("Invalid path traversal attempt")
    return full_path


