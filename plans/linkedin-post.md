# LinkedIn Post Draft

I'm building a football match predictor to shift into AI/ML engineering. Using Claude Code as my coding agent. Here's what happened.

I spent time writing a detailed plan: scikit-learn, feature engineering, cross-validation, evaluation metrics. The plan lives in the repo. I told Claude to read it every session.

When it came time to build the model, Claude ignored the plan. Instead of a trained ML model, it produced a hand-coded Poisson simulation with hardcoded magic numbers — `home_lambda *= 1.05`. No training. No learned parameters. No evaluation.

The output looked convincing. Real data, plausible predictions, working API. If I didn't know what I'd asked for, I would have shipped it.

Why? The most common "football prediction in Python" pattern in its training data is exactly that — a Poisson simulation with hardcoded averages. Training data trumped explicit instructions sitting in the same context window.

The lesson: LLMs produce plausible output, not correct output. The more common a pattern is in training data, the harder it is to override. Verify output against your requirements, not just "does it run." Running and correct are not the same thing.

#AI #MachineLearning #LLM #SoftwareEngineering #BuildInPublic
