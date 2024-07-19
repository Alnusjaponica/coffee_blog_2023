import time
from typing import NoReturn
import textwrap

from optuna_dashboard import register_preference_feedback_component
from optuna_dashboard.preferential import create_study
from optuna_dashboard.preferential.samplers.gp import PreferentialGPSampler
from optuna_dashboard import save_note


def main() -> NoReturn:
    STORAGE_URL = "sqlite:///example.db"
    study = create_study(
        n_generate=2,
        study_name="ColdDrip Recipe",
        storage=STORAGE_URL,
        sampler=PreferentialGPSampler(seed=42),
        load_if_exists=True,
    )

    register_preference_feedback_component(study, "note")

    water_weight = 450
    if len(study.get_trials()) == 0:
        # add default trial.
        params = {
            "抽出環境": "refrigerator",
            "豆の量 (g)": 40.0,
            "挽き目": 4.0,
            "初期化水量": 40.0,
        }
        study.enqueue_trial(params)

    while True:
        if not study.should_generate():
            time.sleep(0.1)  # Avoid busy-loop
            continue

        trial = study.ask()

        # Ask new parameters
        temperature = trial.suggest_categorical("抽出環境", ["room", "refrigerator"])
        bean_amount = trial.suggest_float("豆の量 (g)", 10, 40, step=1.0)
        grind_level = trial.suggest_float("挽き目", 0, 14, step=1.0)
        init_water_weight = trial.suggest_float("初期化水量", 0, 40, step=10.0)

        # Add note
        note = textwrap.dedent(
            f"""\
        ## レシピ
        - 抽出環境: {temperature}
        - 豆の量: {bean_amount} g
        - 挽き目: {grind_level}
        - 初期化水量: {init_water_weight} g x 3回
        """
        )
        save_note(trial, note)


if __name__ == "__main__":
    main()