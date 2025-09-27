import random
import re
from tqdm import tqdm
import datasets
from gpt4all import GPT4All
from src.core.llm_adapter import LLMInterface

dataset_field_map = {
    "google/boolq": {"question": "question", "context": "passage", "answer": "answer"},
    "lighteval/piqa": {"question": "goal", "context": ["sol1", "sol2"], "answer": "label"},
}

dataset_task_type = {
    "google/boolq": "boolq",
    "lighteval/piqa": "multi_class",
}

class Evaluator:
    def __init__(self, model_name: str, dataset_name: str, seed: int, sample_size: int = 500, device='cpu'):
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.seed = seed
        self.sample_size = sample_size
        self.device = device

        self.model = GPT4All(model_name, device=device)
        self.llm = LLMInterface(self.model)

        self.dataset = datasets.load_dataset(dataset_name, split="validation")
        self.field_map = dataset_field_map[self.dataset_name]
        self.task_type = dataset_task_type.get(self.dataset_name, "boolq")

    def sample_dataset(self):
        random.seed(self.seed)
        indices = random.sample(range(len(self.dataset)), self.sample_size)
        return self.dataset.select(indices)

    def normalize_answer(self, text: str):
        text = text.strip().lower()
        if self.task_type == "boolq":
            if "yes" in text:
                return "yes"
            elif "no" in text:
                return "no"
            else:
                return "unknown"
        elif self.task_type.startswith("multi_class"):
            match = re.search(r"\b\d\b", text)
            if match:
                return int(match.group())
            else:
                return -1
        else:
            return text

    def normalize_gold(self, gold_raw):
        if self.task_type == "boolq":
            return "yes" if gold_raw else "no"
        elif self.task_type.startswith("multi_class"):
            return int(gold_raw)
        else:
            return gold_raw

    def build_prompt(self, item):
        if self.task_type == "boolq":
            question = item[self.field_map["question"]]
            context = item[self.field_map["context"]]
            return f"Answer the following question strictly with 'yes' or 'no'.\n\nContext: {context}\nQuestion: {question}\nAnswer:"
        elif self.task_type == "multi_class":  # PIQA
            goal = item[self.field_map["question"]]
            sol1 = item[self.field_map["context"][0]]
            sol2 = item[self.field_map["context"][1]]
            return f"Goal: {goal}\nOption 0: {sol1}\nOption 1: {sol2}\nAnswer with 0 or 1 only:"
        else:
            return str(item)

    def evaluate(self):
        data = self.sample_dataset()
        correct = 0
        for item in tqdm(data):
            prompt = self.build_prompt(item)
            response = self.llm.generate(prompt)
            pred = self.normalize_answer(response)
            gold = self.normalize_gold(item[self.field_map["answer"]])
            if pred == gold:
                correct += 1
            ## To print faliure case
            # else:
            #     print(f"prompt: {prompt}\nresponse: {response}\ntrue answer: {gold}")
        return correct / self.sample_size