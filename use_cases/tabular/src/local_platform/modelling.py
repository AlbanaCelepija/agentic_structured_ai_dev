import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin

from aequitas.engine import Aequitas
import aequitas.tools as tools


def train_baseline(
    training_sample: pd.DataFrame,
    parameters: dict,
    transform_dictionary: dict,
    classifier_type: str = "Decision_Tree",
    classifier_params: dict = {"random_state": 42, "min_samples_leaf": 10},
) -> ClassifierMixin:
    """Train a classifier with no fairness intervention."""
    aeq = Aequitas(training_sample, parameters)
    aeq.transform_instructions(transform_dictionary)

    class_attribute = parameters["class_attribute"]["name"]
    aeq.transform()
    clf = tools.train_classifier(
        aeq.dataset, class_attribute, classifier_type, classifier_params
    )
    return clf


def train_with_reweighting(
    training_sample: pd.DataFrame,
    parameters: dict,
    transform_dictionary: dict,
    sensitive_attribute: str,
    classifier_type: str = "Decision_Tree",
    classifier_params: dict = {"random_state": 42, "min_samples_leaf": 10},
) -> ClassifierMixin:
    """Train a classifier using the aequitas re-weighting technique.

    Re-weighting assigns per-sample weights that balance the joint distribution of the
    sensitive attribute and the class label, countering statistical parity violations
    without modifying the underlying data.
    """
    aeq = Aequitas(training_sample, parameters)
    aeq.transform_instructions(transform_dictionary)

    clf = aeq.mitigation_model(
        method="re-weighting",
        sensitive_attribute=sensitive_attribute,
        classifier=classifier_type,
        classifier_params=classifier_params,
    )
    return clf


