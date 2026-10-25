"""Reproducible positive-projected predator-prey simulation and controllers."""
from dataclasses import dataclass
from collections import deque
from statistics import pstdev
from math import isfinite
import random


def clamp(x, lo=0.0, hi=1.0):
    return min(hi, max(lo, x))


@dataclass(frozen=True)
class Params:
    growth: float = 1.0
    capacity: float = 1.0
    predation: float = 1.2
    conversion: float = 0.65
    mortality: float = 0.35
    target: float = 0.55
    initial_prey: float = 0.5
    initial_predator: float = 0.45
    dt: float = 0.02
    steps: int = 1500
    disturbance: float = 0.1
    disturbance_period: int = 50

    def validate(self):
        for name in ('growth', 'capacity', 'predation', 'conversion', 'mortality', 'target', 'dt'):
            if not isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f'{name} must be positive and finite')
        for name in ('initial_prey', 'initial_predator', 'disturbance'):
            if not isfinite(getattr(self, name)) or getattr(self, name) < 0:
                raise ValueError(f'{name} must be nonnegative and finite')
        if self.steps <= 0 or self.disturbance_period <= 0:
            raise ValueError('steps and disturbance_period must be positive')


def disturbances(p, seed):
    rng = random.Random(seed)
    signal = []
    for i in range(p.steps):
        if i % p.disturbance_period == 0:
            current = rng.uniform(-p.disturbance, p.disturbance)
        signal.append(current)
    return signal


def policy_action(policy, prey, target, history, max_rate=0.25):
    """Candidate PCC operationalization, NOT a canonical EBID definition."""
    pressure = clamp((target - prey) / target)
    # Rolling variation of differences: a volatility proxy, not mathematical chaos.
    chaos_proxy = clamp(pstdev(history) / 0.05) if len(history) > 1 else 0.0
    if policy == 'none':
        action = 0.0
    elif policy == 'fixed':
        action = 0.05
    elif policy == 'pcc_adaptive':
        demand = 0.16 * pressure + 0.06 * chaos_proxy
        action = clamp(demand, 0.0, max_rate) if demand >= 0.03 else 0.0
    else:
        raise ValueError(f'Unknown policy: {policy}')
    return action, pressure, chaos_proxy


def simulate(policy='pcc_adaptive', p=None, seed=42, signal=None):
    p = p or Params()
    p.validate()
    signal = disturbances(p, seed) if signal is None else list(signal)
    if len(signal) != p.steps or any(not isfinite(v) for v in signal):
        raise ValueError('Disturbance signal must contain finite values for every step')
    prey, predator = p.initial_prey, p.initial_predator
    recent = deque(maxlen=20)
    rows = []
    for i, disturbance in enumerate(signal):
        u, pressure, volatility = policy_action(policy, prey, p.target, tuple(recent))
        rows.append({'policy': policy, 'time': i * p.dt, 'prey': prey,
                     'predator': predator, 'intervention': u, 'pressure': pressure,
                     'chaos_proxy': volatility, 'control': u / 0.25,
                     'disturbance': disturbance})
        dx = p.growth * prey * (1 - prey / p.capacity) - p.predation * prey * predator + u + disturbance
        dy = p.conversion * p.predation * prey * predator - p.mortality * predator
        next_prey = max(0.0, prey + p.dt * dx)
        next_predator = max(0.0, predator + p.dt * dy)
        if not (isfinite(next_prey) and isfinite(next_predator)):
            raise FloatingPointError('Population diverged')
        recent.append(next_prey - prey)
        prey, predator = next_prey, next_predator
    return rows


def metrics(rows, target, dt):
    n = len(rows)
    if not n:
        raise ValueError('No rows')
    return {'mean_absolute_target_error': sum(abs(r['prey'] - target) for r in rows) / n,
            'cumulative_intervention': sum(r['intervention'] * dt for r in rows),
            'low_prey_fraction': sum(r['prey'] < target / 2 for r in rows) / n,
            'final_prey': rows[-1]['prey'], 'final_predator': rows[-1]['predator']}
