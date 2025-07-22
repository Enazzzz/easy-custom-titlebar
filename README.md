# Easy Custom Titlebar

A plug-and-play, beautiful custom title bar and window manager for Pygame/Win32 apps on Windows. This package lets you add a modern, draggable, resizable, borderless window with custom minimize, maximize, and close buttons to your Pygame project—no prior experience required!

---

## What is this?

**Easy Custom Titlebar** replaces the default Windows title bar in your Pygame app with a fully custom, modern one. It gives you:
- A borderless window with a custom title bar
- Native-feeling minimize, maximize, and close buttons (with icons)
- Drag-to-move and drag-to-resize window support
- Optional vertical scrolling support
- All required icons and assets included
- Simple, beginner-friendly API

You do NOT need to know anything about Windows APIs, Pygame window management, or custom drawing. Just follow the steps below!

---

## Installation

1. **Install with pip:**
   ```bash
   pip install easy_custom_titlebar
   ```
   This will also install `pygame` and `pywin32` if you don't have them.

2. **(Optional) If installing locally:**
   - Download or clone this repo.
   - In the project folder, run:
     ```bash
     pip install .
     ```

---

## Quick Start Example

Create a new Python file (e.g., `my_app.py`) and paste this code:

```python
from easy_custom_titlebar import CustomTitleBarWindow

def draw_content(screen, width, height, scroll_y):
    import pygame
    # Fill the area below the titlebar with a color
    pygame.draw.rect(screen, (60, 80, 120), (0, window.titlebar_height, width, height-window.titlebar_height))
    font = pygame.font.SysFont("Consolas", 24)
    text = font.render(f"Hello, World! Scroll: {scroll_y}", True, (255, 255, 255))
    screen.blit(text, (20, window.titlebar_height + 20))

if __name__ == "__main__":
    window = CustomTitleBarWindow(width=800, height=500, title="My App", enable_scroll=True)
    window.run(draw_content)
```

Run it with:
```bash
python my_app.py
```

You’ll see a modern window with a custom titlebar, working buttons, and your content below!

---

## Full API Reference

### Class: `CustomTitleBarWindow`

#### Constructor
```python
CustomTitleBarWindow(
    width=1200,
    height=700,
    title="",
    enable_scroll=False,
    titlebar_color=None,
    button_color=None,
    button_hover_color=None,
    button_icon_color="white",
    titlebar_border=False,
    titlebar_border_color=(0,0,0),
    titlebar_border_thickness=1,
    titlebar_font_family="Consolas",
    titlebar_font_size=28,
    titlebar_font_bold=True,
    left_notch_width=0,
    titlebar_height=40,
    close_button_color=(200,0,0),
    close_button_hover_color=(255,0,0),
    minmax_button_hover_color=None,
    window_icon=None,
    minimize_icon=None,
    maximize_icon=None,
    restore_icon=None,
    close_icon=None,
    custom_buttons=None
)
```

#### Parameter Details (Exhaustive)

| Parameter                  | Type         | Default         | Description |
|----------------------------|--------------|-----------------|-------------|
| **width**                  | int          | 1200            | Width of the window in pixels. |
| **height**                 | int          | 700             | Height of the window in pixels. |
| **title**                  | str          | ""              | The text displayed in the titlebar. |
| **enable_scroll**          | bool         | False           | If True, enables vertical scrolling via mouse wheel or arrow keys. The scroll value is passed to your draw_content function. |
| **titlebar_color**         | tuple/str    | (25,25,25)      | Background color of the titlebar. Accepts an RGB tuple (e.g., (30,30,30)) or a hex string (e.g., "#1e1e1e"). |
| **button_color**           | tuple/str    | titlebar_color  | Background color of the titlebar buttons. Accepts RGB tuple or hex string. |
| **button_hover_color**     | tuple/str    | (150,150,150)   | Background color of buttons when hovered. |
| **button_icon_color**      | str          | "white"         | Icon color for all titlebar buttons. Use "white" or "black". |
| **titlebar_border**        | bool         | False           | If True, draws a border at the bottom of the titlebar. |
| **titlebar_border_color**  | tuple        | (0,0,0)         | Color of the titlebar border (RGB tuple). |
| **titlebar_border_thickness**| int        | 1               | Thickness of the titlebar border in pixels. |
| **titlebar_font_family**   | str          | "Consolas"      | Font family for the titlebar text. Any font available on your system. |
| **titlebar_font_size**     | int          | 28              | Font size for the titlebar text. |
| **titlebar_font_bold**     | bool         | True            | Whether the titlebar text is bold. |
| **left_notch_width**       | int          | 0               | Width in pixels to leave as a "notch" at the left of the titlebar (for a sidebar). |
| **titlebar_height**        | int          | 40              | Height of the titlebar in pixels. Set only at creation. |
| **close_button_color**     | tuple        | (200,0,0)       | Background color of the close (X) button. |
| **close_button_hover_color**| tuple       | (255,0,0)       | Background color of the close button when hovered. |
| **minmax_button_hover_color**| tuple      | (150,150,150)   | Background color of minimize/maximize buttons when hovered. |
| **window_icon**            | str/None     | None            | Path to a custom window/taskbar icon (PNG/ICO). If None, uses default. |
| **minimize_icon**          | str/None     | None            | Path to a custom minimize button icon. If None, uses default. |
| **maximize_icon**          | str/None     | None            | Path to a custom maximize button icon. If None, uses default. |
| **restore_icon**           | str/None     | None            | Path to a custom restore button icon. If None, uses default. |
| **close_icon**             | str/None     | None            | Path to a custom close button icon. If None, uses default. |
| **custom_buttons**         | list[dict]   | None            | List of custom button dicts to add to the titlebar. Each dict can have: `icon` (path), `label` (str), `tooltip` (str), `callback` (function), and `left` (int, px offset from left). |

##### **Parameter Usage Examples**
- To set a dark blue titlebar: `titlebar_color=(10,20,40)` or `titlebar_color="#0a1428"`
- To use black icons: `button_icon_color="black"`
- To add a sidebar notch: `left_notch_width=60`
- To add a custom button:
  ```python
  def on_help():
      print("Help clicked!")
  window = CustomTitleBarWindow(custom_buttons=[{"icon": "my_icon.png", "tooltip": "Help", "callback": on_help, "left": 200}])
  ```

---

### Methods & Properties

#### `run(draw_content=None)`
- **Starts the window’s main loop.**
- `draw_content` is a function you provide that draws your app’s content. It should accept `(screen, width, height, scroll_y)`.
- The window handles all titlebar and button logic for you.
- **Example:**
  ```python
  def draw_content(screen, width, height, scroll_y):
      import pygame
      y_offset = window.titlebar_height
      pygame.draw.rect(screen, (100, 100, 200), (0, y_offset, width, height-y_offset))
      font = pygame.font.SysFont("Arial", 24)
      text = font.render("This is my app!", True, (255,255,255))
      screen.blit(text, (30, y_offset + 20))
  window.run(draw_content)
  ```

#### `set_title(title)`
- **Changes the window’s title text.**
- Call this at any time to update the titlebar text.
- **Example:** `window.set_title("New Title")`

#### `maximize_window()`
- **Maximizes or restores the window.**
- You can call this to programmatically maximize or restore the window.
- **Example:** `window.maximize_window()`

#### `minimize_window()`
- **Minimizes the window.**
- **Example:** `window.minimize_window()`

#### `close_window()`
- **Closes the window.**
- **Example:** `window.close_window()`

#### `titlebar_height` (property)
- **Returns the height of the titlebar.**
- Read-only after creation. Use this to align your content below the titlebar.
- **Example:**
  ```python
  y_offset = window.titlebar_height
  pygame.draw.rect(screen, (60, 80, 120), (0, y_offset, width, height-y_offset))
  ```

---

### Helper: `resource_path(filename)`
- **Returns the absolute path to a built-in asset (icon/image) in the package.**
- Use this to load icons from the package’s assets folder.
- **Example:**
  ```python
  from easy_custom_titlebar import resource_path
  icon_path = resource_path('close_white.png')
  my_icon = pygame.image.load(icon_path)
  ```

---

## Usage Tips & Best Practices
- Always use `window.titlebar_height` to align your content below the titlebar.
- Use the `custom_buttons` parameter to add extra buttons (e.g., Help, Settings) to the titlebar.
- Use the `enable_scroll` parameter if your content is scrollable.
- For best results, use PNG icons with transparency for custom buttons.
- All color parameters accept both RGB tuples and hex strings.
- The titlebar height, font, and notch width are fixed at creation for reliability.

---

## Parameter Details & Notes

- **titlebar_color, button_color, button_hover_color**: Accept either an RGB tuple (e.g., `(30,30,30)`) or a hex string (e.g., `"#1e1e1e"`). If not set, sensible defaults are used.
- **button_icon_color**: Use `"white"` or `"black"` to select the icon variant for all buttons.
- **titlebar_border**: If `True`, draws a border at the bottom of the titlebar. You can customize its color and thickness.
- **titlebar_font_family, titlebar_font_size, titlebar_font_bold**: Control the font used for the titlebar text.
- **left_notch_width**: If greater than 0, leaves a "notch" at the left of the titlebar for a sidebar. The notch area is filled with the window background color. To visually merge a sidebar, draw your sidebar in the content area at x=0, width=`left_notch_width`.
- **titlebar_height**: Set only at creation. All titlebar drawing, button placement, and content alignment will use this value. Cannot be changed after window creation.
- **Button hitboxes and drawing**: All button hitboxes and drawing are recalculated every frame, so they always match the current titlebar height and notch settings.
- **All drawing is handled for you**: You do not need to manually handle button clicks or titlebar logic—just use `window.run(draw_content)`.

---

## How to Access the Built-in Icons/Assets

All icons (minimize, maximize, restore, close) are included in the package. To get the path to an asset:

```python
from easy_custom_titlebar import resource_path
icon_path = resource_path('close_white.png')
```

You can use this path to load the icon in your own code if needed.

---

## Troubleshooting & FAQ

**Q: I get an error about missing DLLs or win32gui.**
- Make sure you’re on Windows and have run `pip install easy_custom_titlebar` (which installs `pywin32`).

**Q: The window doesn’t have rounded corners!**
- Rounded corners require Windows 11. On older Windows, the window will still work, just with square corners.

**Q: The buttons don’t show up or look weird.**
- Make sure you’re not running in a virtual environment that blocks image loading, and that the assets are included (they are by default).

**Q: How do I draw my own UI below the titlebar?**
- Just use the `draw_content` function you pass to `run()`. Draw anything you want on the `screen` surface, starting at `window.titlebar_height` (below the titlebar).

**Q: Can I use this for a game?**
- Yes! Just draw your game in `draw_content`.

**Q: Can I change the titlebar color or icons?**
- You can edit the package’s assets or code, or fork the repo for more customization.

**Q: Can I change the titlebar height after the window is created?**
- No. For simplicity and reliability, the titlebar height is fixed at creation time.

---

## Project Structure

```
Easy Custom Titlebar/
  ├── easy_custom_titlebar/
  │     ├── __init__.py
  │     ├── custom_titlebar.py
  │     └── assets/
  │           ├── *.png, *.ico
  ├── setup.py
  ├── MANIFEST.in
  ├── README.md
```

- **easy_custom_titlebar/**: Main package code and assets.
- **assets/**: All icons and images used by the titlebar.
- **setup.py**: Packaging and installation config.
- **MANIFEST.in**: Ensures assets are included in the package.
- **README.md**: Documentation and usage.

---

## Contributing

Contributions are welcome! Please open an issue or pull request for bug fixes, new features, or documentation improvements.

- Fork the repo and create your branch from `main`.
- Add your feature or fix, and include tests if possible.
- Ensure your code is clean and well-documented.
- Submit a pull request with a clear description of your changes.

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. Please be respectful and inclusive in all interactions.

---

## License

MIT 