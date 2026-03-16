# Assignment 4 – ML Model CI/CD Pipeline

## Overview

This repository demonstrates a **GitHub Actions CI/CD pipeline** for an ML project, built as part of Assignment 4 in the MLOps course. The pipeline automatically validates the ML environment, runs linting checks, tests the model setup, and uploads project documentation as a build artifact — all triggered on every push to any branch **except** `main`.

This work is grounded in the concepts from **Chapter 4 – Continuous Delivery for Machine Learning Models** (Practical MLOps, Noah Gift & Alfredo Deza, O'Reilly 2021).

---

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ml-pipeline.yml   # GitHub Actions CI/CD workflow
├── model.py                  # ML model placeholder (linted by CI)
├── requirements.txt          # Python dependencies
└── README.md                 # This file (also uploaded as CI artifact)
```

---

## Pipeline Steps

| Step | Action | Purpose |
|------|--------|---------|
| Checkout Code | `actions/checkout@v4` | Clones the repository onto the runner |
| Set up Python | `actions/setup-python@v5` | Configures Python 3.10 |
| Install Dependencies | `pip install -r requirements.txt` | Installs torch and pylint |
| Linter Check | `pylint model.py` | Enforces code quality standards |
| Model Dry Test | `python -c "import torch; ..."` | Verifies the ML environment is ready |
| Upload Project Documentation | `actions/upload-artifact@v4` | Saves README.md as artifact `project-doc` |

---

## Bug Report: Fixing the Original Broken YAML

The original workflow YAML provided in the assignment contained **4 bugs**. Below is a detailed analysis of each bug and how it was resolved.

---

### Bug 1 – Global Indentation Errors (Critical / Syntax)

**Location:** Entire file  
**Severity:** Fatal — the workflow cannot be parsed at all

**Description:**  
The original YAML was completely flat with no indentation. YAML is a whitespace-sensitive format, and GitHub Actions workflows require strict 2-space indentation to express hierarchy. Every key that belongs to a parent must be indented under it.

**Original (broken):**
```yaml
on:
push:
branches: main
pull_request:

jobs:
validate-and-test:
runs-on: ubuntu-latest
steps:
- name: Set up Python
uses: actions/setup-python@v5
with:
python-version: '3.10'
```

**Fixed:**
```yaml
on:
  push:
    branches-ignore:
      - main
  pull_request:

jobs:
  validate-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
```

**Why it matters:**  
Without correct indentation, the YAML parser cannot determine the relationship between keys. GitHub Actions would reject the file entirely with a workflow syntax error.

---

### Bug 2 – Missing `actions/checkout` Step (Logic / Runtime)

**Location:** Under `steps:`, before any other steps  
**Severity:** Fatal — all file-dependent steps will fail

**Description:**  
The original workflow had no step to check out the repository code. When a GitHub Actions runner starts, it is a blank virtual machine with no access to the repository files. The `actions/checkout` action must be the **first step** to clone the code onto the runner. Without it, `pip install -r requirements.txt` fails immediately because `requirements.txt` does not exist on the runner.

**Original (broken):**
```yaml
steps:
  - name: Set up Python        # checkout is completely absent
    uses: actions/setup-python@v5
```

**Fixed:**
```yaml
steps:
  - name: Checkout Code
    uses: actions/checkout@v4   # clones repo onto runner first

  - name: Set up Python
    uses: actions/setup-python@v5
```

**Why it matters:**  
As explained in Chapter 4 of *Practical MLOps*, the first step in any CI/CD job must make the code available. Without checkout, every subsequent step that depends on repository files will fail with a "file not found" error.

---

### Bug 3 – Incomplete "Linter Check" Step (Syntax)

**Location:** The `- name: Linter Check` step  
**Severity:** Fatal — workflow fails to parse

**Description:**  
The `Linter Check` step had only a `name:` field and no execution directive. In GitHub Actions, every step **must** have either a `run:` key (for shell commands) or a `uses:` key (for actions). A step with only `name:` is syntactically invalid and causes the entire workflow to fail to load.

**Original (broken):**
```yaml
- name: Linter Check
            # No run: or uses: — this step does nothing and breaks the YAML
```

**Fixed:**
```yaml
- name: Linter Check
  run: pylint --disable=R,C model.py
```

**Why it matters:**  
Linting is one of the core quality gates in a CI pipeline. Chapter 4 emphasizes that each step should have a distinct, clear responsibility. Leaving this step empty defeats its purpose and breaks the entire workflow.

---

### Bug 4 – Incorrect `on:` Trigger Configuration (Logic)

**Location:** The `on:` block, `push.branches` key  
**Severity:** Logical — pipeline runs on the wrong branches

**Description:**  
The original configuration used `branches: main`, which restricts the push trigger to **only** the `main` branch. The assignment requirement is the opposite: the pipeline should run on every push to **all branches except `main`**. Using `branches-ignore` achieves this correctly. The `pull_request:` trigger remains unchanged so it still fires on all pull requests.

**Original (broken):**
```yaml
on:
  push:
    branches: main    # only runs on main — wrong requirement
  pull_request:
```

**Fixed:**
```yaml
on:
  push:
    branches-ignore:
      - main          # runs on all branches EXCEPT main
  pull_request:
```

**Why it matters:**  
In a standard GitFlow or trunk-based development model, feature branches are where active development happens. Validating code *before* it reaches `main` is the entire point of CI. Running the pipeline only on `main` is too late — bugs should be caught earlier. As Chapter 4 discusses, continuous evaluation at every step of the process is a core CI/CD principle.

---

## Reflection: What Chapter 4 Teaches Us

Chapter 4 of *Practical MLOps* covers **Continuous Delivery for Machine Learning Models**. The central insight is that CI/CD is not just a DevOps concept — it is the foundation of reliable MLOps. Key takeaways relevant to this assignment:

1. **Automation over manual execution:** Running checks manually is error-prone and inconsistent. GitHub Actions automates the validation pipeline so that every code change is verified the same way, every time.

2. **Separation of concerns in pipeline steps:** Each step should have one clear responsibility. This makes failures easier to diagnose. The bugs in the assignment demonstrate exactly this — an incomplete step (Bug 3) or a missing prerequisite step (Bug 2) makes the entire pipeline opaque and unreliable.

3. **Artifacts for traceability:** Uploading build artifacts (like `README.md` as `project-doc`) provides a traceable record of what documentation was present at the time of each run — important for model reproducibility.

4. **Branch strategy matters:** Triggering CI on feature branches (not just `main`) ensures that problems are caught before code reaches production. This directly reflects the "constant evaluation" philosophy the authors describe using the analogy of an athlete monitoring injuries daily.

---

## GitHub Actions Workflow File

See [`.github/workflows/ml-pipeline.yml`](.github/workflows/ml-pipeline.yml) for the full corrected workflow.

---

## GitHub Repository

[https://github.com/Baherbb/assignment_4_mlops](https://github.com/Baherbb/assignment_4_mlops)
