# Ping Pong Arena

Mobile-friendly ping pong game built with Python + pygame, compiled to WebAssembly via pygbag.

## Features

- Classic ping pong vs bot
- 3 difficulty levels (Easy / Normal / Hard)
- Normal mode (first to 5) and Infinite mode
- 9 ball colors
- 2 languages (English / Russian)
- Sound effects
- Personal stats (Wins counter, Best score)
- Rage mode — bot plays harder when you lead by 3+
- Cute cheering crowd with emotions

## Play online

After deployment via GitHub Pages, the game will be available at:

```
https://YOUR-USERNAME.github.io/REPO-NAME/
```

## Local development

```bash
pip install pygame
python main.py
```

(Note: `main.py` is the web-adapted version with fixed 360x720 size. Original phone version is in `pingpong.py` if present.)

## Build for web yourself

```bash
pip install pygbag
pygbag --build main.py
```

Output goes to `build/web/`.

## Auto-deploy

Push to `main` branch → GitHub Actions builds with pygbag → publishes to GitHub Pages automatically.

## Privacy

Each player's settings (name, stats, preferences) are saved in their **own browser** via IndexedDB. Players don't see each other's data.
