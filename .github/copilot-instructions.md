# IMScreenNotation – AI Coding Guide

- **What this app is:** PyQt5 screen-annotation overlay with floating toolbar, global hotkeys (pynput), and JSON import/export. Entry point is `main.py` → `AnnotationTool` wires canvas, toolbar, hotkeys, tray, rulers, and config.
- **Core architecture:**
  - `canvas/DrawingCanvas` owns rendering state: `CanvasProperties` (current tool/color/thickness/opacity + text styles), `CanvasEventHandler` (mouse press/move/release logic per tool), `CanvasStateManager` (undo/redo up to 50 states, JSON import/export via `shape.to_dict()`/`from_dict()`), `CanvasPainter` (actual drawing), and shape classes in `shapes/*` (line/rect/circle/arrow/freehand/filled/point/laser/text/eraser/ruler/image).
  - `manager/*` splits concerns: `WindowManager` sets frameless full-screen transparent host and toggles canvas visibility; `TransparencyManager` flips Qt `WindowTransparentForInput` and syncs canvas opacity + toolbar button states; `ToolManager` updates `tool_button_group`, sets canvas tool, status bar hints, and single-draw mode; `ConfigManager` bridges `config.py` (QColor ↔ list JSON) to canvas/toolbar.
  - `toolbar/AnnotationToolbar` is decomposed into theme (`toolbar_theme`), widgets (`toolbar_widgets`), events (`toolbar_events`), scrollable layout and sizing (`toolbar_scrollable`). Buttons and sliders are stored on `tool_button_group`, `toggle_*` buttons, etc.; size recalcs via `ToolbarSizeManager`.
  - `hotkey/HotkeyManager` listens with pynput in a background thread; uses `<ctrl>+<alt>+...` strings, parses modifiers strictly, and emits Qt signal `hotkey_triggered` to execute callbacks on the UI thread. `HotkeyHandler/HotkeySettingsDialog` register defaults from `config.json`.
  - `ruler` package builds line/circle rulers; canvas caches `ruler_*` settings and applies updates to existing ruler shapes when `RulerManager` emits `ruler_settings_changed`.
  - `FileOperations` handles JSON import/export via dialogs; status messages use `constants.STATUS_MESSAGE_TIMEOUT`.
- **Config & state:**
  - User settings live in `config.json`; first run auto-creates it. Colors must be `QColor` in-memory and are serialized to RGBA lists—keep that contract when adding fields. Text styling defaults live in `config.py`/`constants.DEFAULT_CONFIG` and are applied through `ConfigManager._apply_text_config`.
  - Undo/redo skips transient shapes (laser, eraser) and caps stacks at 50; single-draw mode clears shapes and stacks before appending the new shape.
- **Adding or changing tools/features:**
  - New tools generally require: shape class with `to_dict/from_dict` in `shapes/*`, painter support in `canvas/painter.py`, event handling in `canvas/events.py` (press/move/release), registration in `ToolManager` + toolbar button, and hotkey mapping in `HotkeyHandler`/config defaults. For persisted shapes, ensure JSON serialization and state manager deserialization.
  - When altering text/image/ruler behaviors, also update corresponding dialogs (`text_edit`, `text_style`, `image_settings_dialog`) and keep toolbar controls/hotkeys consistent.
- **Run & debug:**
  - Dev run: `python main.py` (requires PyQt5, pynput; virtualenv under `.venv`). Window is frameless, always-on-top, and installs an event filter to keep toolbar foreground—expect focus quirks if debugging dialogs.
  - Global hotkeys rely on pynput; failures there usually stem from missing permissions or layout differences—check `HotkeyManager.key_to_string` and config hotkey strings.
- **Builds:**
  - Preferred: `python build_optimized.py` → PyInstaller using `IMScreenNotation_safe.spec`; script optionally finds UPX and prints size stats. Keep `required_files` and spec `hidden-imports` in sync when adding modules; otherwise PyInstaller will miss them.
  - Minimal fallback build is embedded in `build_optimized.py` (`build_with_minimal_approach`) if the spec path breaks.
- **File paths to know:** `main.py`, `canvas/`, `shapes/`, `toolbar/`, `hotkey/`, `manager/`, `config.py` + `config.json`, `constants.py`, `build_optimized.py`, `IMScreenNotation_safe.spec`.

If anything here feels off or incomplete, tell me which part to refine.