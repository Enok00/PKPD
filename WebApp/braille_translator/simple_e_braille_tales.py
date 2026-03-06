import argparse
import pathlib
import re
import sys
import tempfile
import types
import warnings
from pathlib import Path

import cv2
import numpy as np

try:
    __import__("torchvision.models.utils")
except ModuleNotFoundError:
    import torch.hub

    torchvision_models_utils = types.ModuleType("torchvision.models.utils")
    torchvision_models_utils.load_state_dict_from_url = torch.hub.load_state_dict_from_url
    sys.modules["torchvision.models.utils"] = torchvision_models_utils

from fastai.vision.all import load_learner


if sys.platform.startswith("win"):
    pathlib.PosixPath = pathlib.WindowsPath


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal OCR pipeline for Perkins braille page images using Model_Perkins_Brailler_acc9997."
    )
    parser.add_argument("--input-dir", type=Path, default=Path("OCR Raw Data"))
    parser.add_argument("--output-dir", type=Path, default=Path("OCR Predictions"))
    parser.add_argument("--model", type=Path, default=Path("Model_Perkins_Brailler_acc9997"))
    parser.add_argument("--x-min", type=int, default=282)
    parser.add_argument("--char-width", type=int, default=60)
    parser.add_argument("--char-height", type=int, default=90)
    parser.add_argument("--x-gap", type=int, default=12)
    parser.add_argument("--columns", type=int, default=41)
    parser.add_argument("--line-threshold", type=int, default=15)
    parser.add_argument("--max-lines", type=int, default=19)
    parser.add_argument("--crop-margin", type=int, default=10)
    return parser.parse_args()


def collect_images(input_dir: Path) -> list[Path]:
    return [
        file_path
        for file_path in sorted(input_dir.iterdir())
        if file_path.suffix.lower() in {".jpg", ".jpeg"}
    ]


def detect_lines(
    gray: np.ndarray,
    char_height: int,
    line_threshold: int,
    max_lines: int,
) -> list[tuple[int, int]]:
    image_filtered = np.where(gray == 255, 0, 1)
    y_sum = np.sum(image_filtered, axis=0)
    img_height = gray.shape[1]

    best_lines: list[tuple[int, int]] = []
    best_cutoff = None

    for cutoff in range(30, 300, 10):
        y_pixels = np.where(y_sum > cutoff)[0]
        lines: list[tuple[int, int]] = []
        for idx in range(len(y_pixels) - 1):
            if y_pixels[idx + 1] - y_pixels[idx] <= line_threshold:
                continue

            y_max = int(y_pixels[idx])
            y_min = int(y_max - char_height)

            if y_min <= 0 or y_max + char_height >= img_height:
                continue
            if lines and (y_min - lines[-1][0] < char_height):
                continue

            lines.append((y_min, y_max))

        if len(lines) > max_lines:
            continue

        if len(lines) > len(best_lines):
            best_lines = lines
            best_cutoff = cutoff
        elif len(lines) == len(best_lines) and best_cutoff is not None and cutoff < best_cutoff:
            best_lines = lines
            best_cutoff = cutoff

    return best_lines


def crop_rectangles_for_page(
    text_image: np.ndarray,
    lines_y: list[tuple[int, int]],
    x_min: int,
    char_width: int,
    x_gap: int,
    columns: int,
    crop_margin: int,
) -> tuple[list[np.ndarray], list[list[tuple[int, int, int, int]]], np.ndarray]:
    overlay = text_image.copy()
    gray = cv2.cvtColor(text_image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    page_crops: list[np.ndarray] = []
    per_line_boxes: list[list[tuple[int, int, int, int]]] = []

    # Reverse so lines are processed top -> bottom, matching reading order.
    for y_min, y_max in reversed(lines_y):
        line_boxes: list[tuple[int, int, int, int]] = []

        current_x = x_min
        for _ in range(columns):
            x0 = current_x
            x1 = current_x + char_width
            current_x += char_width + x_gap

            y0_crop = max(0, x0 - crop_margin)
            y1_crop = min(h, x1 + crop_margin)
            x0_crop = max(0, y_min - crop_margin)
            x1_crop = min(w, y_max + crop_margin)

            crop = gray[y0_crop:y1_crop, x0_crop:x1_crop]
            page_crops.append(crop)

            line_boxes.append((x0, x1, y_min, y_max))
            cv2.rectangle(overlay, (y_min, x0), (y_max, x1), (0, 255, 0), 2)

        per_line_boxes.append(line_boxes)

    return page_crops, per_line_boxes, overlay


def derive_output_name(first_image: Path) -> str:
    matches = list(re.finditer("-", first_image.name))
    if matches:
        return first_image.name[: matches[-1].start()]
    return first_image.stem


def labels_to_page_text(labels: list[str], line_count: int, columns: int) -> str:
    lines: list[str] = []
    idx = 0
    for _ in range(line_count):
        line_chars = labels[idx : idx + columns]
        idx += columns
        line_string = "".join(line_chars).rstrip("⠀")
        lines.append(line_string)
    return "\n".join(lines).strip("\n")


def main() -> None:
    args = parse_args()
    cwd = Path.cwd()

    input_dir = (cwd / args.input_dir).resolve()
    output_dir = (cwd / args.output_dir).resolve()
    model_path = (cwd / args.model).resolve()

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    if not input_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    image_paths = collect_images(input_dir)
    if not image_paths:
        raise FileNotFoundError(f"No .jpg/.jpeg files found in {input_dir}")

    output_name = derive_output_name(image_paths[0])
    result_dir = output_dir / output_name
    result_dir.mkdir(parents=True, exist_ok=True)

    rectangles_dir = cwd / "Page image files with rectangles simple"
    rectangles_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading model: {model_path}")
    warnings.filterwarnings(
        "ignore",
        message="load_learner` uses Python's insecure pickle module",
        category=UserWarning,
    )
    try:
        learn = load_learner(model_path)
    except Exception as exc:
        message = str(exc)
        if "fastcore.transform" in message or "fastai>=2.8.0" in message:
            raise RuntimeError(
                "Model compatibility error. Install legacy-compatible dependencies with:\n"
                "  .\\env\\Scripts\\python.exe -m pip install -r requirements.txt\n"
                "Expected: fastai<2.8 and fastcore<1.8 for this model export."
            ) from exc
        raise

    all_pages: list[str] = []

    for page_index, image_path in enumerate(image_paths, start=1):
        text_image = cv2.imread(str(image_path))
        if text_image is None:
            print(f"Skipping unreadable image: {image_path.name}")
            continue

        gray = cv2.cvtColor(text_image, cv2.COLOR_BGR2GRAY)
        lines_y = detect_lines(
            gray=gray,
            char_height=args.char_height,
            line_threshold=args.line_threshold,
            max_lines=args.max_lines,
        )
        if not lines_y:
            print(f"No lines detected on page: {image_path.name}")
            continue

        crops, _, overlay = crop_rectangles_for_page(
            text_image=text_image,
            lines_y=lines_y,
            x_min=args.x_min,
            char_width=args.char_width,
            x_gap=args.x_gap,
            columns=args.columns,
            crop_margin=args.crop_margin,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            char_files: list[Path] = []
            for i, crop in enumerate(crops):
                char_file = tmp_path / f"{i}.jpg"
                cv2.imwrite(str(char_file), crop)
                char_files.append(char_file)

            dl = learn.dls.test_dl([str(p) for p in char_files], shuffle=False)
            with learn.no_bar(), learn.no_logging():
                preds = learn.get_preds(dl=dl)[0].softmax(dim=1)
            preds_argmax = preds.argmax(dim=1).tolist()
            labels = [learn.dls.vocab[preds_argmax[i]] for i in range(len(preds_argmax))]

        labels = ["⠀" if label == "empty_braille_cell" else label for label in labels]
        page_text = labels_to_page_text(labels, line_count=len(lines_y), columns=args.columns)
        all_pages.append(page_text)

        rect_file = rectangles_dir / f"{image_path.stem} with character rectangles.jpg"
        cv2.imwrite(str(rect_file), overlay)
        print(f"[{page_index}/{len(image_paths)}] Processed: {image_path.name}")

    output_file = result_dir / f"{output_name}-OCR results simple.txt"
    output_file.write_text("\n\n".join(all_pages), encoding="utf-8")
    print(f"OCR text written to: {output_file}")


if __name__ == "__main__":
    main()