```python
import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# Function to detect data drift
def detect_data_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame):
    # Define column mapping (you might need to adjust this based on your dataset)
    column_mapping = ColumnMapping()

    # Create a data drift report
    data_drift_report = Report(metrics=[DataDriftPreset()])

    # Run the report
    data_drift_report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)

    # Get the results
    results = data_drift_report.as_dict()

    return results

# Example usage
if __name__ == "__main__":
    # Example reference and current data
    reference_data = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5],
        "feature2": [5, 4, 3, 2, 1]
    })

    current_data = pd.DataFrame({
        "feature1": [2, 3, 4, 5, 6],
        "feature2": [4, 3, 2, 1, 0]
    })

    # Detect data drift
    drift_results = detect_data_drift(reference_data, current_data)

    # Print results
    print(drift_results)
```