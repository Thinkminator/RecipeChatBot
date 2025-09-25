import inspect
from gpt4all import GPT4All
print("GPT4All.generate signature:")
print(inspect.signature(GPT4All.generate))
print()
print("Doc:")
print((GPT4All.generate.__doc__ or "")[:1000])
