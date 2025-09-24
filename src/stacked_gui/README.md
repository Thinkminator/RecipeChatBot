
# Stacked Tkinter GUI (Modular)

This project demonstrates a *stacked-Frame* router pattern with **separate files per page**.

## Structure
```
stacked_gui/
├── app.py                 # Router (single Tk root), entry point
├── backend.py             # Shared logic (tries to import your real backends; falls back to stubs)
└── pages/
    ├── __init__.py
    ├── base_page.py       # BasePage with Back button & header
    ├── mode_selection_page.py
    ├── input_type_page.py
    ├── text_page.py
    └── speech_page.py
```

## Run
```bash
cd stacked_gui
python app.py
```

- If you already have real modules like `src.core.nlu`, `src.core.knowledge`, `src.core.huggingface_api`,
  or `src.core.custom_llm`, `backend.py` will import them automatically.
- Otherwise, stub implementations are used so the UI still runs.

## Notes
- **Back** is handled by the router (`App.back`) with a simple history stack.
- To add a new page: create a `pages/your_page.py` with a class `YourPage(BasePage)`, register it in `pages/__init__.py`, then add it to the loop in `app.py`.
- If you need to free resources when leaving a page, implement `on_hide()`.
- If you need to update a page on entry, implement `on_show(...)`.
