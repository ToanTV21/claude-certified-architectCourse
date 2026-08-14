# Exercises — Agents and Workflows

- `01_chaining_workflow.py` — Chaining workflow: output of one Claude call feeds
  into the next (draft -> critique -> revise).
- `02_routing_workflow.py` — Routing workflow: classify the input, then dispatch
  to a different prompt/handler per category.
- `03_evaluator_optimizer_workflow.py` — Evaluator-Optimizer workflow: producer
  drafts a docstring, evaluator grades it and gives feedback, loop until accepted
  or max iterations.
- `04_parallelization_workflow.py` — Parallelization workflow: evaluate a part
  against multiple materials in parallel Claude calls, then aggregate into one
  final recommendation.
- `05_environment_inspection_exercise.py` — Environment inspection: read-before-write
  pattern — read a target file's current content first, then ask Claude to propose a
  change that matches the existing structure/convention.
