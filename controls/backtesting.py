def pd_backtest(actual_defaults, predicted_pd):
    return {
        "observed_defaults": actual_defaults.sum(),
        "expected_defaults": predicted_pd.sum(),
        "difference": actual_defaults.sum() - predicted_pd.sum(),
    }


def ecl_backtest(ecl_estimated, writeoffs, recoveries):
    realized_loss = writeoffs - recoveries
    return {
        "estimated_ecl": ecl_estimated,
        "realized_loss": realized_loss,
        "error": realized_loss - ecl_estimated,
    }
