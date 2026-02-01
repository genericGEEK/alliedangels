# extras/utils.py
import io
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]

# Your resize target
MAX_WIDTH = 900          # preferred
HARD_MAX_WIDTH = 2000     # absolute cap
JPEG_QUALITY = 85


def normalize_ext(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return "jpg" if ext == "jpeg" else ext


def owner_label(instance) -> str:
    """
    Label used in filenames. Uses content_type.model if available.
    e.g. "event", "eventseries", "blogpost", "banner"
    """
    if getattr(instance, "content_type_id", None):
        return instance.content_type.model
    return "unassigned"


def image_upload(instance, filename: str) -> str:
    """
    Requirement #3:
    - single path: images/
    - filename makes it easy to tell owner type + object_id
    - include a uuid to avoid collisions

    Example:
      images/event-42-8f3a91c2.jpg
    """
    label = owner_label(instance)
    oid = instance.object_id or "noid"
    ext = normalize_ext(filename)

    # We will output JPEG after processing anyway, so force .jpg
    ext = "jpg"

    short = uuid.uuid4().hex[:8]
    return f"media/{label}-{oid}-{short}.{ext}"


def validate_landscape_image(file_obj):
    """
    Requirement #2:
    Landscape only. (width > height)
    """
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        w, h = img.size
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")

    if w <= h:
        raise ValidationError("Image must be landscape orientation (width greater than height).")


def process_image_to_jpeg(file_obj, *, max_width=MAX_WIDTH, hard_max_width=HARD_MAX_WIDTH, quality=JPEG_QUALITY) -> ContentFile:
    """
    Requirement #1:
    Resize for web:
      - prefer <= 1200px wide
      - never exceed 2000px wide
    Output JPEG to keep size sane and consistent (good for S3/CDN).

    Returns ContentFile containing processed JPEG bytes.
    """
    file_obj.seek(0)
    img = Image.open(file_obj)

    # Convert to RGB (JPEG can't store alpha)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    w, h = img.size

    # If someone uploads a massive image, cap it hard first.
    # Then bring it down to preferred max_width.
    target_w = min(max_width, hard_max_width)
    if w > hard_max_width:
        scale = hard_max_width / float(w)
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    # Now thumbnail down to preferred bounds (keeps aspect ratio)
    # Since all are landscape, height bound can be derived (safe cap)
    img.thumbnail((target_w, 1200), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)
    buffer.seek(0)

    return ContentFile(buffer.read())
