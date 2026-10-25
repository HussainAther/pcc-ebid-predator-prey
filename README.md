# PCC–EBID Predator–Prey

Exploratory, reproducible experiments on **Pressure–Chaos–Control (PCC)** inspired adaptation in synthetic predator–prey systems. This is a *hypothesis-generating prototype*, not a validated or canonical EBID implementation and not ecological management advice.

## Research question

Can a bounded adaptive intervention reduce prey target deviation under stochastic environmental disturbances compared with no support or fixed support, and at what intervention cost?

## Quick start

```bash
python -m pip install -e '.[test,plot]'
python -m pytest -q
python -m pcc_predator_prey.experiment --output results/baseline.csv --seed 42 --plot
```

The experiment generates `.csv` time series, `.json` metrics, and optionally a `.png` figure. All three policies experience the *same* seeded disturbance sequence.

## Model

Normalized prey `x` and predator `y` follow a capacity-limited Lotka–Volterra-style discrete Euler model:

```
dx/dt = r*x*(1-x/K) - a*x*y + u + d(t)
dy/dt = b*a*x*y - m*y
```

- **Pressure**: clipped prey deficit relative to a target.
- **Chaos proxy**: clipped recent volatility of prey increments. This is **not** dynamical chaos or a Lyapunov exponent.
- **Control**: fraction of available intervention capacity used.
- **EBID-inspired policy**: bounded, thresholded feedback from measured pressure and volatility. This is a *candidate operationalization* rather than an assertion of the framework's definitive equations.

`u` is additive prey-support effort, never predator removal. Populations are projected to be nonnegative. Environmental disturbances are piecewise constant and seeded. The default numbers are illustrative rather than fitted to a particular ecosystem.

## Baselines and evaluation

- `none`: no support
- `fixed`: constant rate of 0.05
- `pcc_adaptive`: rate from weighted pressure and volatility, capped at 0.25

Metrics: mean absolute prey target error, cumulative intervention effort, low-prey fraction, and final prey/predator population. Consider the full trade-off: lower target error does not alone establish a better ecological policy.

## Validity limits and planned work

No empirical calibration, observation noise, delays, predator-welfare objective, extinction mechanism, or claim of external validity. The hard projection and forward Euler scheme may distort extreme regimes. Next studies should include held-out parameters, paired multi-seed confidence intervals, fixed-effort comparisons, delayed control, feature ablations, intervention-cost penalties, and integration checks against more accurate solvers.

## License

MIT.
