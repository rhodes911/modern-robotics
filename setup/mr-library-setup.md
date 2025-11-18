# Modern Robotics (MR) Python Library Setup

The courses use the MR library provided by the authors. To keep licensing simple, this repo does not redistribute it.

Get the library:
- Visit http://modernrobotics.org
- Download the MR Python library (ZIP) and extract it into `modern-robotics/mr/`
  - After extraction, this folder should contain Python modules like `modern_robotics.py` (or similar structure provided by the authors).

Usage in your code:
```python
# Prefer explicit import paths to avoid ambiguity
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "mr"))

import modern_robotics as mr  # according to the library’s module name
```

Notes
- Keep MR read-only; build your own implementations in `src/robotics/` so you can compare/learn.
- If you use MATLAB/Mathematica variants, follow the course instructions separately.
