## Plan: Scaffold `spec_test` with GE Data Profiling

Create a new AI product at [enhanced_mlops/framework/library/use_cases/spec_test](enhanced_mlops/framework/library/use_cases/spec_test), implement only the `local_platform` data profiling path, and add Great Expectations quantity checks limited to min/max row-count thresholds (your selected v1 scope). The plan mirrors existing conventions from [tabular local data prep](enhanced_mlops/framework/library/use_cases/tabular/src/local_platform/data_preparation.py), keeps metadata wiring compatible with the framework’s operation runner in [guided_ui/app.py](enhanced_mlops/guided_ui/app.py#L484), and avoids DH-specific execution logic unless needed later.

**Steps**
1. Scaffold product structure under [enhanced_mlops/framework/library/use_cases/spec_test](enhanced_mlops/framework/library/use_cases/spec_test) by copying essential template assets from [aipc_template](enhanced_mlops/framework/library/aipc_template) and preserving lifecycle folders (`docs`, `metadata`, `src/local_platform`, `src/local_platform/artifacts/data`, `src/local_platform/artifacts/report`, `src/local_platform/model`, `src/local_platform/experiments`).
2. Create/update [spec_test metadata](enhanced_mlops/framework/library/use_cases/spec_test/metadata/aipc_local.yaml) with a `data_profiling` operation mapped to `src/local_platform/data_preparation.py` and a method symbol (e.g., `data_profiling_quantity_ge`) plus configuration artifact for row-count bounds (`min_rows`, `max_rows`).
3. Implement GE profiling operation in [spec_test local data prep](enhanced_mlops/framework/library/use_cases/spec_test/src/local_platform/data_preparation.py): load dataset artifact, run Great Expectations row-count expectation, return structured profiling output/report artifact, and keep function signature aligned with framework invocation style used in `run_operation`.
4. Add dependency updates in [spec_test requirements](enhanced_mlops/framework/library/use_cases/spec_test/requirements.txt) for `great_expectations` and any minimal runtime companions; keep dependency delta small and local to this use case.
5. Add documentation pointers in [spec_test datasheet](enhanced_mlops/framework/library/use_cases/spec_test/docs/Datasheet.md) and/or operation notes so profiling outputs and threshold semantics are explicit for reuse.
6. Apply the prompt constraint from [system prompt file](agentic_structured_ai_dev/src/agents/mcp_host/mcp_servers/prompts/planner_agent_prompts/system_prompt_cot.txt): include source citations `[1]`, `[2]` at the end of generated code blocks/comments where this project expects generated provenance.

**Verification**
- Run targeted import/exec sanity for the new module in `spec_test/src/local_platform/data_preparation.py`.
- Execute profiling with a small sample dataset and confirm row-count validation status and report artifact generation under `artifacts/report`.
- Validate metadata-to-method wiring by confirming operation method names and paths match `aipc_local.yaml`.
- Optional UI-path check: ensure `spec_test` is discoverable by the guided flow and operation invocation resolves.

**Decisions**
- Chose new product scaffold (`use_cases/spec_test`) over modifying template in-place.
- Chose `local_platform` only (no DH implementation in this iteration).
- Chose v1 quantity validation scope: min/max row count only.
