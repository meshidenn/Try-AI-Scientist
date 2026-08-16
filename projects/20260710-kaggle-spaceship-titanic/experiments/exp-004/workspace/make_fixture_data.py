from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def make_passenger_ids(n: int, start_group: int = 1) -> list[str]:
    group_ids = np.repeat(np.arange(start_group, start_group + (n // 4) + 2), 4)[:n]
    positions = np.tile(np.arange(1, 5), (n // 4) + 2)[:n]
    return [f"{group:04d}_{pos:02d}" for group, pos in zip(group_ids, positions)]


def make_frame(n: int, seed: int, include_target: bool) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    home_planet = rng.choice(["Earth", "Europa", "Mars"], n, p=[0.55, 0.23, 0.22])
    destination = rng.choice(
        ["TRAPPIST-1e", "55 Cancri e", "PSO J318.5-22"],
        n,
        p=[0.68, 0.2, 0.12],
    )
    cryo_sleep = rng.random(n) < np.where(home_planet == "Europa", 0.42, 0.28)
    age = np.clip(rng.normal(31, 15, n), 0, 79)
    vip = rng.random(n) < np.where(home_planet == "Europa", 0.08, 0.02)
    deck = rng.choice(list("ABCDEFGT"), n)
    side = rng.choice(["P", "S"], n)
    cabin_num = rng.integers(0, 1900, n)
    spending_base = rng.gamma(1.8, 450, n)
    zero_spend = cryo_sleep | (rng.random(n) < 0.18)

    frame = pd.DataFrame(
        {
            "PassengerId": make_passenger_ids(n),
            "HomePlanet": home_planet,
            "CryoSleep": cryo_sleep.astype(object),
            "Cabin": [f"{d}/{num}/{s}" for d, num, s in zip(deck, cabin_num, side)],
            "Destination": destination,
            "Age": age.round(1),
            "VIP": vip.astype(object),
            "RoomService": np.where(zero_spend, 0, spending_base * rng.random(n)),
            "FoodCourt": np.where(zero_spend, 0, spending_base * rng.random(n)),
            "ShoppingMall": np.where(zero_spend, 0, spending_base * rng.random(n)),
            "Spa": np.where(zero_spend, 0, spending_base * rng.random(n)),
            "VRDeck": np.where(zero_spend, 0, spending_base * rng.random(n)),
            "Name": [f"Passenger {idx}" for idx in range(n)],
        }
    )

    for col in ["HomePlanet", "CryoSleep", "Cabin", "Destination", "Age", "VIP"]:
        missing_mask = rng.random(n) < 0.025
        frame.loc[missing_mask, col] = np.nan

    if include_target:
        logit = (
            -0.15
            + 1.35 * cryo_sleep.astype(float)
            + 0.4 * (home_planet == "Europa").astype(float)
            + 0.2 * (destination == "55 Cancri e").astype(float)
            - 0.00035 * frame[["RoomService", "Spa", "VRDeck"]].sum(axis=1)
            + 0.15 * (side == "S").astype(float)
            + rng.normal(0, 0.45, n)
        )
        probability = 1 / (1 + np.exp(-logit))
        frame["Transported"] = rng.random(n) < probability

    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=Path("data"), type=Path)
    parser.add_argument("--train-rows", default=1200, type=int)
    parser.add_argument("--test-rows", default=400, type=int)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    train = make_frame(args.train_rows, args.seed, include_target=True)
    test = make_frame(args.test_rows, args.seed + 1, include_target=False)
    sample = pd.DataFrame({"PassengerId": test["PassengerId"], "Transported": False})

    train.to_csv(args.out_dir / "train.csv", index=False)
    test.to_csv(args.out_dir / "test.csv", index=False)
    sample.to_csv(args.out_dir / "sample_submission.csv", index=False)


if __name__ == "__main__":
    main()
