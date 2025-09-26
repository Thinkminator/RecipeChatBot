import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import argparse
from src.core.llm_adapter import gpt4all_model_list
from src.evaluation.evaluator import Evaluator

import torch

def main():
    parser = argparse.ArgumentParser(description="Evaluate GPT4All model on BoolQ dataset")
    parser.add_argument("--model", type=str, default=gpt4all_model_list[1],
                        help="Model name from gpt4all_model_list")
    parser.add_argument("--dataset", type=str, default="google/boolq",
                        help="Dataset name (default: BoolQ)")
    parser.add_argument("--seed", type=int, required=True,
                        help="Random seed (last 3 digits of matric number)")
    parser.add_argument("--sample_size", type=int, default=500,
                        help="Number of samples to evaluate (default: 500)")
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)
    print(f"Use model: {args.model}; dataset: {args.dataset}")
    evaluator = Evaluator(args.model, args.dataset, args.seed, args.sample_size, device)
    acc = evaluator.evaluate()
    print("results:")
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Accuracy: {acc:.2%}")


if __name__ == "__main__":
    main()
