## Dino Game (Professionalized Structure)

### Run
- Python 3.10+
- Install deps:
```bash
pip install -r requirements.txt
```
- Start game:
```bash
python game.py
```

### Project Structure
- `runner/` — package with modules:
  - `config.py` — constants and tuning
  - `assets.py` — robust asset loading
  - `obstacles.py` — obstacle entity
  - `game.py` — main game loop class
  - `main.py` — entry for running
- `assets/` — put `background.png`, `character.png` here (fallback: project root)
- `game.py` — thin entrypoint
- `requirements.txt` — dependencies

### Notes
- Logging configured in `runner/main.py`.
- Types added; code is organized for easier testing and maintenance.

