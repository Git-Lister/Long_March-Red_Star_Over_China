# 长征：红星照耀中国 · Long March: Red Star Over China

*Historical survival narrative, collectivist decisions, harrowing battles.*

## Quick Start (after scaffold generation)
```bash
python -m venv venv
venv\\Scripts\\activate      # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Project Structure
```
long-march/
├── src/              # main source
│   ├── core/         # engine, party, config
│   ├── combat/       # battle simulation
│   ├── narrative/    # events, prologue, AI
│   ├── ui/           # terminal/graphical UI
│   └── main.py       # entry point
├── data/             # map.json, events.json
├── saves/            # game saves
├── assets/           # images, fonts
├── tests/            # unit tests
├── models/           # optional local LLM
├── setup.py
├── requirements.txt
└── README.md
```

## Development
- All stub methods raise `NotImplementedError` until implemented.
- The scaffold is solid; now implement one module at a time.

*The Long March begins with a single step—and a solid scaffold.*

