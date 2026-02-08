A warning to vibe coders.

I'm using Claude Code to build a football match predictor. I wrote a proper plan for it. Trained model, learned parameters, evaluation pipeline. The plan lives in the repo and Claude reads it every session.

When I asked it to build the model it ignored all of that. Gave me a Poisson simulation with hardcoded multipliers instead. No training step. No learned weights. Just `home_lambda *= 1.05`.

The scary part is it worked. Real data, plausible predictions, clean API. I would have shipped it if I couldn't read the code myself.

If you can't verify the output matches what you actually asked for, the agent is driving and you're just watching.
