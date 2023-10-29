# coffee_blog_2023

## How to run
```bash
pip install "optuna>=3.3.0" "optuna-dashboard[preferential]>=0.13.0b1"

python recipe_generator.py &
optuna-dashboard sqlite:///example.db
```