import numpy as np
from sklearn.metrics import ndcg_score

queries =[
    "What is the capital of France?",
    "Who painted the Mona Lisa?",
    "What is the highest mountain in the world?",
]
ground_truth = [
    [0, 1, 2],  # indices of relevant documents for query 1
    [3, 4],     # indices of relevant documents for query 1
    [5, 6, 7]   # indices of relevant documents for query 1
]

retrieved = [
    [1, 5, 0, 2, 8, 9, 3, 4, 6, 7],  # ranked list of retrieved document indices for query 1]
    [1, 5, 0, 2, 8, 9, 3, 4, 6, 7],  # ranked list of retrieved document indices for query 1]
    [1, 5, 0, 2, 8, 9, 3, 4, 6, 7],  # ranked list of retrieved document indices for query 1]
]

# recall@k
def calculate_recall_at_k(ground_truth, retrieved, k):
    """ Calculate Recall@k for a set of queries"""
    recall_scores = []
    for gt, ret in zip(ground_truth, retrieved):
        num_relevant = len(gt)
        retrieved_k = ret[:k]
        num_relevant_retrieved = len(set(gt).intersection(set(retrieved_k)))
        recall = (num_relevant_retrieved / num_relevant if num_relevant > 0 else 0)
        recall_scores
    return np.mean(recall_scores)