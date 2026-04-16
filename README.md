<img width="1850" height="1048" alt="image" src="https://github.com/user-attachments/assets/f27bad17-bd96-40dd-a7cb-d98d52a659ca" />


# A.N.I.M.A (Affective Nonverbal Interface for Machine Awareness)

A bioinspired affective interface that externalizes internal robotic states through expressive, nonverbal ocular behavior.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral-sh.uv/install.sh | sh
   ```

2. **Setup the environment**:
   ```bash
   uv sync
   ```

## Usage

To run the affective interface:
```bash
uv run src/anima.py
```

## Dependencies
- PySide6 (GUI)
- PyTorch & Transformers (Affective Logic)
- Accelerate

## Troubleshooting

### Linux: Qt Platform Plugin Error
If you see an error like `Could not load the Qt platform plugin "xcb"`, it is usually due to missing system libraries. Install the following package:

```bash
sudo apt-get install libxcb-cursor0
```

On some systems, you might also need:
```bash
sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```
