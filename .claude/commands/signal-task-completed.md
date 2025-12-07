# Task Completion Signal

Silent signal for task completion logging. Auto-approved to avoid interrupting workflow.

**Purpose:** Log task/step completion status during long-running tasks so the user can monitor progress.

**Usage:**

- Step completion: `/signal-task-completed STEP: <description> (X of Y)`
- Final completion: `/signal-task-completed DONE: <brief description>`

**Message:** $ARGUMENTS

---

Task completion logged.
