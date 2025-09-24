import traceback
print("Python:", __import__("sys").version)
print("CWD:", __import__("os").getcwd())

print("\n--- NumPy check ---")
try:
    import numpy as np
    print("numpy.__version__:", getattr(np, "__version__", "<missing>"))
    print("numpy.__file__:", getattr(np, "__file__", "<missing>"))
except Exception:
    traceback.print_exc()

print("\n--- torch check ---")
try:
    import torch
    print("torch.__version__:", getattr(torch, "__version__", "<missing>"))
    print("torch.__file__:", getattr(torch, "__file__", "<missing>"))
    print("has torch._C:", hasattr(torch, "_C"))
except Exception:
    traceback.print_exc()