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
        study_name="Coffee recipe",
        storage=STORAGE_URL,
        sampler=PreferentialGPSampler(seed=42),
        load_if_exists=True,
    )

    register_preference_feedback_component(study, "note")

    water_weight = 150
    speed = 2 # g/sec

    if len(study.get_trials()) == 0:
        # add default trial.
        # ref: https://www.youtube.com/watch?v=G7vxam3T5mQ&t=68s
        params = {
            "お湯の温度(℃)": 86,
            "豆の量 (g)/お湯の量(g)": 12/150,
            "ミルのクリック数": 18,
            "蒸らし時間(sec)": 20,
            "蒸らしのお湯の量(g)": 20,
        }
        study.enqueue_trial(params)

    while True:
        if not study.should_generate():
            time.sleep(0.1)  # Avoid busy-loop
            continue

        trial = study.ask()

        # Ask new parameters
        temperature = trial.suggest_float("お湯の温度(℃)", 80, 95, step=1.0)
        bean_per_water = trial.suggest_float("豆の量 (g)/お湯の量(g)", 0.053, 0.1, step=0.01) # 8/150-15/150
        click_count = trial.suggest_float("ミルのクリック数", 16, 24, step=1.0)
        steaming_time = trial.suggest_float("蒸らし時間(sec)", 0, 40, step=5.0)
        steaming_water_weight = trial.suggest_float("蒸らしのお湯の量(g)", 10, 30, step=10.0)

        # compute paramters
        bean_weight = int(bean_per_water*water_weight)

        # Add note
        note = textwrap.dedent(
            f"""\
        ## レシピ
        - お湯の温度(℃): {int(temperature)}
        - ミルのクリック数: {int(click_count)}
        - 豆の量(g): {int(bean_weight)}
        - 蒸らしのお湯の量(g): {int(steaming_water_weight)}
        - 蒸らし時間(sec): {int(steaming_time)}
        - 抽出量(g): {int(water_weight)}
        """
        )
        save_note(trial, note)


if __name__ == "__main__":
    main()