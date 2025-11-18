# SnipingToolAlt

FYI This is still being worked on and isn't finished. I thought I would just open source it now.

## Why this was made?

This was made because I frankly don't really like Windows and macOS's snipping tool feature and I feel like it could be a bit better + this is quite fun to make :)

## Building & Running

### Prerequisites

- Python 3.10+ (3.9 might work but has PyQt6 issues on macOS)
- pip or a Python package manager

### Installation

1. Clone the repo:
```bash
git clone <repo-url>
cd SnipingToolAltt
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running

```bash
python -m src
```

Or directly:
```bash
python src/__main__.py
```

### Default Keybinds

- **Ctrl+Shift+S** - Toggle overlay
- **Ctrl+Shift+F** - Fullscreen capture (when overlay is active)

Screenshots are saved to `~/Pictures/Screenshots/` by default.

## Features

- Global hotkey overlay for region selection
- Automatic screenshot capture and clipboard copy
- Fullscreen capture support
- Configurable keybinds
- System tray integration
- Sequential screenshot naming
- Cross-platform support (Windows, macOS, Linux)

## To-Do

- [ ] Clean up code
- [ ] Make sure it's fine for all OS's
- [ ] Add a better keybind selecting interface
- [ ] Overall improvements

---

Sorry for the ass code btw ik :skull:
