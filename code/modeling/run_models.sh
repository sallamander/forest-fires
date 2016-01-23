#!/bin/bash

echo 'Running Logistic Model'
tmux new -d -s logit 'python code/modeling/run_model.py logit code/modeling/geo_time_done.csv'

echo 'Running Random Forest Model'
tmux new -d -s random_forest 'python code/modeling/run_model.py random_forest code/modeling/geo_time_done.csv'

echo 'Running Gradient Boosting Model'
tmux new -d -s g_boosting 'python code/modeling/run_model.py gradient_boosting code/modeling/geo_time_done.csv'
