# Modern Tetris Game

A modern implementation of Tetris that runs in web browsers using Pygame and Pygbag.

## Features

- Responsive design for both desktop and mobile
- Touch and keyboard controls
- Modern metallic visual style
- Progressive difficulty
- Score system
- Offline support
- Cross-browser compatibility

## Requirements

- Python 3.8+
- Pygame 2.5.2
- Pygbag 0.8.3

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

To run the game locally:
```bash
python main.py
```

## Web Deployment

To deploy the game to web:
```bash
pygbag main.py
```
Then open http://localhost:8000 in your browser.

## Controls

### Keyboard
- Left/Right Arrow: Move piece horizontally
- Up Arrow: Rotate piece
- Down Arrow: Soft drop
- Space: Hard drop

### Touch Controls
- Swipe left/right: Move piece
- Tap: Rotate piece
- Swipe down: Soft drop
- Virtual buttons available on screen

## License

MIT License
