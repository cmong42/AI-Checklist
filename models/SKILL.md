---
name: ai-assistant-pipeline
description: 'Takes a task, breaks it down into simple steps, and outputs them.'
---

# Instructions

1. Given the following task <INSERT_TASK_HERE>, format it as a coding problem, that is, rephrase it as a problem statement that can be solved with code.

2. Treating the reformatted task as a coding problem, break it down into small, manageable steps that can be sequentially solved.

3. Output the steps you generated in layman's terms, and ensure that they are clear and easy to understand. Your output should be formatted in a JSON format (see example below). Include subtasks if applicable.

```json
{
  "steps": [
    "Step 1": {
      <INSERT_SUBSTEP_1_HERE>,
      <INSERT_SUBSTEP_2_HERE>,
      <INSERT_SUBSTEP_3_HERE>
    },
    "Step 2: <INSERT_STEP_2_HERE>",
    "...",
    "Step N: <INSERT_STEP_N_HERE>"
  ]
}
```