from pathlib import Path
import io
import tarfile
import zipfile


MAX_FILE_SIZE = 100 * 1024 * 1024
MAX_TOTAL_SIZE = 500 * 1024 * 1024


SUPPORTED_TEXT = {
    ".log",
    ".txt",
    ".out",
    ".err",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".csv",
}


def safe_path(base: Path, name: str) -> Path:
    """
    Prevent archive path traversal such as:
    ../../etc/passwd
    """

    target = (base / name).resolve()

    if not str(target).startswith(str(base.resolve())):
        raise ValueError(f"Unsafe archive path: {name}")

    return target


def decode_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode("utf-8", errors="replace")


def extract_uploaded_file(uploaded_file):
    """
    Returns:
        list[tuple[str, str]]
        (filename, text)
    """

    filename = uploaded_file.name
    data = uploaded_file.getvalue()

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(
            f"{filename} exceeds the {MAX_FILE_SIZE // 1024 // 1024} MB limit."
        )

    lower = filename.lower()

    # ZIP
    if lower.endswith(".zip"):
        results = []

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            total_size = 0

            for info in z.infolist():

                if info.is_dir():
                    continue

                total_size += info.file_size

                if total_size > MAX_TOTAL_SIZE:
                    raise ValueError("Archive exceeds total extraction limit.")

                if info.file_size > MAX_FILE_SIZE:
                    continue

                name = Path(info.filename).name

                if not name:
                    continue

                raw = z.read(info)

                results.append(
                    (
                        name,
                        decode_bytes(raw),
                    )
                )

        return results

    # TAR / TAR.GZ / TGZ
    if (
        lower.endswith(".tar")
        or lower.endswith(".tar.gz")
        or lower.endswith(".tgz")
    ):
        results = []

        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:

            total_size = 0

            for member in tar.getmembers():

                if not member.isfile():
                    continue

                total_size += member.size

                if total_size > MAX_TOTAL_SIZE:
                    raise ValueError("Archive exceeds total extraction limit.")

                if member.size > MAX_FILE_SIZE:
                    continue

                extracted = tar.extractfile(member)

                if extracted is None:
                    continue

                raw = extracted.read()

                name = Path(member.name).name

                if not name:
                    continue

                results.append(
                    (
                        name,
                        decode_bytes(raw),
                    )
                )

        return results

    # Normal text file
    return [(filename, decode_bytes(data))]