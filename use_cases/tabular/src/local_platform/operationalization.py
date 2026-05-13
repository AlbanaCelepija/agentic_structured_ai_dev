def evaluate(
    clf: ClassifierMixin,
    test_sample: pd.DataFrame,
    parameters: dict,
    transform_dictionary: dict,
    verbose: bool = True,
) -> tuple[float, np.ndarray, str]:
    """Test a classifier and report accuracy alongside fairness metrics.

    Returns:
        (accuracy, confusion_matrix, classification_report)
    """
    aeq_test = Aequitas(test_sample, parameters)
    aeq_test.transform_instructions(transform_dictionary)

    class_attribute = parameters["class_attribute"]["name"]
    aeq_test.transform()
    predicted_test_sample, accuracy, confusion, report = tools.test_classifier(
        clf, aeq_test.dataset, class_attribute, verbose=verbose
    )
    aeq_test.inverse_transform()

    aeq_predicted = aeq_test.copy()
    aeq_predicted.set_dataset(predicted_test_sample)
    aeq_predicted.inverse_transform()

    aeq_predicted.statistical_parity(verbose=verbose)
    aeq_predicted.disparate_impact(verbose=verbose)

    prediction = np.array(aeq_predicted.dataset[class_attribute])
    aeq_test.equal_opportunity(prediction, verbose=verbose)
    aeq_test.equal_odds(prediction, verbose=verbose)

    return accuracy, confusion, report