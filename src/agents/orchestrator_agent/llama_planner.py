"""
llama3_planner_profiling.py

Usage:
  - Configure env vars:
      export OPENAI_API_KEY="sk_..."
      # if using an OpenAI-compatible provider:
      export OPENAI_API_BASE="https://api.your-provider.com/v1" 
  - Run:
      python llama3_planner_profiling.py path/to/your.csv
"""

import os
import json
import sys
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ydata-profiling (formerly pandas-profiling)
from ydata_profiling import ProfileReport

# OpenAI client (works with OpenAI and OpenAI-compatible APIs)
import openai

# ---------- Configuration ----------
MODEL = os.getenv("MODEL", "llama3-70b")  # change to model name provided by your host
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")  # optional: e.g. "https://api.groq.com/openai/v1"
if OPENAI_API_BASE:
    openai.api_base = OPENAI_API_BASE
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# If using the "openai" package older versions, ensure ChatCompletion is available.
# ---------- End config ----------

# Allowed actions the planner may request (we will implement)
SUPPORTED_ACTIONS = {
    "summary",              # short dataset summary (rows/cols, memory)
    "dtypes",               # column dtypes overview
    "missing_values",       # missing values per column
    "unique_values",        # cardinality / top categories
    "correlations",         # numeric correlations
    "histograms",           # create simple histograms for numeric cols
    "outliers",             # detect outliers via IQR
    "suggest_transform",    # suggest simple preprocessing actions
    "profile_report"        # produce HTML profile report
}

# Prompt template - ask model to return only a short JSON plan (no chain-of-thought)
PLANNER_PROMPT_TEMPLATE = """
You are a helpful planner for dataset profiling. 

DO NOT provide chain-of-thought, internal reasoning, or any explanations.
ONLY output a single valid JSON object (and nothing else) with the following schema:

{{
  "plan": [
    {{
      "step": <int>,
      "action": <string - one of: {actions}>,
      "params": <object - action-specific parameters, optional>
    }},
    ...
  ]
}}

- Keep the plan concise (3-10 steps).
- Use only supported actions listed above.
- For "histograms", set params: {{"columns": ["col1","col2"], "bins": 30}}
- For "profile_report", set params: {{"title": "Profile for <dataset_name>"}}
- For "suggest_transform", set params: {{"target": "classification" or "regression" or null}}

User query: "{user_query}"
Dataset preview (first rows): {data_preview}

Return only the JSON object.
""".strip()

# ---------- Helper functions ----------

def call_planner_model(user_query: str, data_preview: str) -> Dict[str, Any]:
    """
    Call LLM to get a JSON plan. Returns parsed JSON.
    """
    prompt = PLANNER_PROMPT_TEMPLATE.format(
        actions=", ".join(sorted(SUPPORTED_ACTIONS)),
        user_query=user_query.replace('"', '\\"'),
        data_preview=data_preview.replace('"', '\\"')
    )

    # ChatCompletion
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a strict JSON-output planner. Do not output anything except the JSON object."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.0
    )

    text = resp["choices"][0]["message"]["content"].strip()
    # Parse JSON - be robust in case of stray whitespace
    try:
        plan_json = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner response not valid JSON. Raw response:\n{text}\nError: {e}")
    return plan_json

def validate_plan(plan_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "plan" not in plan_json or not isinstance(plan_json["plan"], list):
        raise ValueError("Plan JSON missing 'plan' list")
    steps = plan_json["plan"]
    for s in steps:
        if "action" not in s or s["action"] not in SUPPORTED_ACTIONS:
            raise ValueError(f"Unsupported or missing action in step: {s}")
    return steps

def execute_step(df: pd.DataFrame, step: Dict[str, Any], dataset_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    action = step["action"]
    params = step.get("params", {}) or {}

    result_meta = {"action": action, "params": params}
    if action == "summary":
        result_meta["n_rows"] = int(df.shape[0])
        result_meta["n_cols"] = int(df.shape[1])
        result_meta["memory_mb"] = float(df.memory_usage(deep=True).sum() / (1024*1024))
    elif action == "dtypes":
        result_meta["dtypes"] = df.dtypes.apply(lambda x: str(x)).to_dict()
    elif action == "missing_values":
        mv = df.isna().sum()
        result_meta["missing_count"] = mv.to_dict()
        result_meta["missing_pct"] = (mv / len(df)).round(4).to_dict()
    elif action == "unique_values":
        cols = params.get("columns", df.columns.tolist())
        uniques = {}
        for c in cols:
            if c in df.columns:
                uniques[c] = {"unique_count": int(df[c].nunique()), "top": df[c].mode().iloc[0] if not df[c].mode().empty else None}
        result_meta["unique"] = uniques
    elif action == "correlations":
        numeric = df.select_dtypes(include=[np.number])
        if numeric.shape[1] >= 2:
            corr = numeric.corr()
            result_meta["correlation_head"] = corr.round(3).iloc[:5, :5].to_dict()
            # Save full correlation to file
            corr.to_csv(f"{dataset_name}_correlation.csv")
            result_meta["correlation_csv"] = f"{dataset_name}_correlation.csv"
        else:
            result_meta["note"] = "Not enough numeric columns for correlation."
    elif action == "histograms":
        cols = params.get("columns", df.select_dtypes(include=[np.number]).columns.tolist())
        bins = int(params.get("bins", 30))
        img_paths = []
        for c in cols:
            if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
                fig, ax = plt.subplots()
                df[c].dropna().hist(bins=bins, ax=ax)
                ax.set_title(f"Histogram {c}")
                img_path = f"{dataset_name}_hist_{c}.png"
                fig.savefig(img_path, bbox_inches="tight")
                plt.close(fig)
                img_paths.append(img_path)
        result_meta["histograms"] = img_paths
    elif action == "outliers":
        cols = params.get("columns", df.select_dtypes(include=[np.number]).columns.tolist())
        outliers = {}
        for c in cols:
            if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
                q1 = df[c].quantile(0.25)
                q3 = df[c].quantile(0.75)
                iqr = q3 - q1
                low = q1 - 1.5 * iqr
                high = q3 + 1.5 * iqr
                mask = (df[c] < low) | (df[c] > high)
                outliers[c] = {"n_outliers": int(mask.sum()), "low": float(low), "high": float(high)}
        result_meta["outliers"] = outliers
    elif action == "suggest_transform":
        # very simple heuristic suggestions
        target = params.get("target")
        suggestions = []
        # missing values
        mv = df.isna().sum()
        for c, cnt in mv.items():
            if cnt > 0:
                suggestions.append({"column": c, "suggest": "impute" if pd.api.types.is_numeric_dtype(df[c]) else "fill_mode"})
        # categorical encoding
        for c in df.select_dtypes(include=["object", "category"]).columns:
            if df[c].nunique() < 20:
                suggestions.append({"column": c, "suggest": "one_hot_if_needed"})
        result_meta["suggestions"] = suggestions
    elif action == "profile_report":
        title = params.get("title", f"Profile report {dataset_name}")
        profile = ProfileReport(df, title=title, explorative=True)
        out_html = f"{dataset_name}_profile.html"
        profile.to_file(out_html)
        result_meta["profile_html"] = out_html
    else:
        result_meta["error"] = "action not implemented"

    return df, result_meta

def run_planner_and_execute(csv_path: str, user_query: str):
    dataset_name = os.path.splitext(os.path.basename(csv_path))[0]
    df = pd.read_csv(csv_path)
    # Provide small preview for the model (first 10 rows as text)
    preview = df.head(8).to_csv(index=False)

    print("Requesting plan from model...")
    plan_json = call_planner_model(user_query=user_query, data_preview=preview)
    steps = validate_plan(plan_json)

    print("Plan received:")
    print(json.dumps(steps, indent=2))

    # Execute steps
    results = []
    for step in steps:
        print(f"Executing step {step.get('step')} action={step.get('action')}")
        _, meta = execute_step(df, step, dataset_name)
        results.append(meta)
        print(" ->", meta.get("note", meta.get("action"), meta))

    # Save results summary
    with open(f"{dataset_name}_plan_results.json", "w", encoding="utf-8") as f:
        json.dump({"user_query": user_query, "steps": steps, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {dataset_name}_plan_results.json")
    print("Done.")

# ---------- Main ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python llama3_planner_profiling.py path/to/dataset.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    # Example user query - in real use accept input or CLI argument
    user_query = (
        "Plan a dataset profiling workflow to assess readiness for ML: "
        "identify key data quality issues, recommend transformations, and produce a profile report."
    )
    run_planner_and_execute(csv_path, user_query)
