
"""
tts.py
Threaded TTS controller with start/stop using pyttsx3.
"""
import threading

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class TTSController:
    def __init__(self):
        self.available = pyttsx3 is not None
        self._engine = None
        self._thread = None
        self._lock = threading.Lock()
        self._on_done = None

    def start(self, text: str, on_done=None) -> bool:
        """Start speaking `text` in a background thread. Returns True if started."""
        if not self.available:
            return False
        with self._lock:
            # If already speaking, stop first
            if self._thread and self._thread.is_alive():
                self._stop_nolock()
            self._on_done = on_done
            self._thread = threading.Thread(target=self._run, args=(text,), daemon=True)
            self._thread.start()
        return True

    def _run(self, text: str):
        try:
            self._engine = pyttsx3.init()
            self._engine.say(text)
            # runAndWait blocks until finished or stop() is called
            self._engine.runAndWait()
        except Exception:
            pass
        finally:
            with self._lock:
                self._engine = None
                cb = self._on_done
                self._on_done = None
        if cb:
            try:
                cb()
            except Exception:
                pass

    def stop(self):
        """Attempt to stop current speech promptly."""
        with self._lock:
            self._stop_nolock()

    def _stop_nolock(self):
        if self._engine is not None:
            try:
                self._engine.stop()  # causes runAndWait() to return
            except Exception:
                pass
