#!/bin/bash

echo 'Running Logistic Model'
tmux new -d -s logit 'python modeling/run_model.py logit modeling/input_df.pkl'

echo 'Running Random Forest Model'
tmux new -d -s random_forest 'python modeling/run_model.py random_forest modeling/input_df.pkl'

echo 'Running Gradient Boosting Model'
tmux new -d -s g_boosting 'python modeling/run_model.py gradient_boosting modeling/input_df.pkl'