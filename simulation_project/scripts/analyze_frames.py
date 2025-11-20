import sys
from pathlib import Path
import re
import cv2
import numpy as np

"""Quick keyframe analyzer.

Copy the keyframe JPGs into a folder inside the repo (e.g.
simulation_project/analysis/keyframes/) then run:

    python scripts/analyze_frames.py simulation_project/analysis/keyframes

Outputs per-frame object presence metrics and color/area summaries.
Designed to detect disappearance, falling (shrinking area), or motion.
"""


COLOR_THRESHOLDS = {
    "red": [((0, 80, 50), (10, 255, 255)), ((170, 80, 50), (180, 255, 255))],  # two ranges
    "green": [((35, 80, 50), (85, 255, 255))],
    "blue": [((95, 80, 50), (130, 255, 255))],
}


def load_images(folder: Path):
    imgs = []
    pattern = re.compile(r"keyframe_\d+_time_.*\.jpg", re.IGNORECASE)
    for f in sorted(folder.iterdir()):
        if pattern.match(f.name):
            img = cv2.imread(str(f))
            if img is not None:
                imgs.append((f.name, img))
    return imgs


def detect_colors(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    results = {}
    for color, ranges in COLOR_THRESHOLDS.items():
        mask_total = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for (lo, hi) in ranges:
            lo_np = np.array(lo, dtype=np.uint8)
            hi_np = np.array(hi, dtype=np.uint8)
            mask = cv2.inRange(hsv, lo_np, hi_np)
            mask_total = cv2.bitwise_or(mask_total, mask)
        # Simple morphological clean
        mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        area = int(np.count_nonzero(mask_total))
        results[color] = area
    return results


def summarize(images):
    if not images:
        print("No keyframe images found in folder.")
        return
    baseline_name, baseline_img = images[0]
    print(f"Baseline frame: {baseline_name}")

    baseline_colors = detect_colors(baseline_img)
    print("Baseline color areas:")
    for c, a in baseline_colors.items():
        print(f"  - {c}: {a} px")

    disappearing_colors = set()
    previous = baseline_colors

    print("\nFrame progression:")
    for name, img in images[1:]:
        areas = detect_colors(img)
        deltas = {c: areas[c] - baseline_colors[c] for c in areas}
        flags = []
        for c, a in areas.items():
            if baseline_colors[c] > 0 and a == 0:
                flags.append(f"{c} gone")
                disappearing_colors.add(c)
            elif baseline_colors[c] > 0 and a < baseline_colors[c] * 0.25:
                flags.append(f"{c} ↓area")
        if not flags:
            flags_str = "stable"
        else:
            flags_str = ", ".join(flags)
        print(f"  {name}: red={areas['red']}, green={areas['green']}, blue={areas['blue']} → {flags_str}")
        previous = areas

    print("\nSummary:")
    if disappearing_colors:
        print("- Colors lost completely: " + ", ".join(sorted(disappearing_colors)))
        print("  Likely objects removed/reset or fell outside view.")
    else:
        print("- No complete disappearance detected.")
    print("- If areas shrink sharply (↓area): possible vertical movement (fall) or occlusion.")
    print("- Validate desk collision: if all areas shrink together quickly, objects may drop below sensor view.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/analyze_frames.py <folder_with_keyframes>")
        return
    folder = Path(sys.argv[1])
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return
    images = load_images(folder)
    summarize(images)


if __name__ == "__main__":
    main()
