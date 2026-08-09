# Exercises — Prompt Evaluation

- `01_prompt_eval_exercise.py` — Exercise on prompt evals: generate a small test dataset,
  run a prompt against it, grade outputs with a simple code-based check.
- `02_model_based_grading_exercise.py` — Model based grading: dùng Claude làm giám khảo
  (LLM-as-judge) để chấm tiêu chí chủ quan (tone, sự đồng cảm) mà code-based grading
  không check được. Dùng lại kỹ thuật prefill + `stop_sequences` từ Session 01 để ép
  grader trả JSON sạch.
