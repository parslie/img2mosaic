from pathlib import Path

from util import VALID_IMAGE_EXTS


def extract_image_paths(base_path: Path, recurse: bool) -> list[Path] | None:
    if base_path.is_file() and base_path.suffix[1:] in VALID_IMAGE_EXTS:
        return [base_path]
    elif base_path.is_dir():
        image_paths = []
        for image_ext in VALID_IMAGE_EXTS:
            glob_pattern = f"**.{image_ext}" if recurse else f"*.{image_ext}"
            image_paths.extend(base_path.glob(glob_pattern))
        return image_paths
    else:
        return None
