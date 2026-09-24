# Generation Pitfalls

## L1 template pitfalls

1. **Template variable not filled**: a missing required variable in the context causes rendering to fail. Rule: validate all placeholders before rendering.

2. **Filename collision**: overwriting an existing target file directly loses code. Rule: check whether the file exists; if it does, read and merge.

3. **Tech stack misdetection**: the detected tech_stack doesn't match reality. Rule: read the user's tech_stack slot first, auto-detection second.

## L2 LLM pitfalls

4. **Hallucinated code**: the LLM generated a non-existent API or dependency. Rule: check imports after generation; report if missing.

5. **Style inconsistency**: generated code differs greatly from the project's existing style. Rule: inject code_style_samples into the prompt.

6. **Out of scope**: generated files not in the plan. Rule: strictly generate only the files specified in sub_tasks.

## Cross-skill collaboration pitfalls

7. **Broken handoff with tdd-guide**: code-generator's code doesn't match tdd-guide's test expectations. Rule: after generating code, automatically call tdd-guide to verify.

8. **Data-format mismatch with code-intent-planner**: a plan JSON format change causes parsing failure. Rule: define a strict JSON Schema.

## Engineering pitfalls

9. **Directory doesn't exist**: the parent directory is missing when writing a generated file. Rule: mkdir -p to ensure the directory exists.

10. **Encoding issues**: UTF-8 encoding errors on Windows. Rule: write all files with encoding="utf-8".

11. **Circular dependency**: L1 and L2 calling each other causes infinite recursion. Rule: set max recursion depth to 1.

12. **Memory leak**: file handles not properly closed when generating many files. Rule: use the with open(...) context manager.
