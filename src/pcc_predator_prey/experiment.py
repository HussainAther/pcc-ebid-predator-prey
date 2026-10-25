"""Compare policies under shared seeded disturbance realization."""
import argparse
import csv
import json
from dataclasses import asdict, replace
from pathlib import Path
from .simulation import Params, disturbances, simulate, metrics


def run(output, seed=42, disturbance=0.1, plot=False):
    p = replace(Params(), disturbance=disturbance)
    p.validate()
    signal = disturbances(p, seed)
    policies = ['none', 'fixed', 'pcc_adaptive']
    rows = []
    summaries = {}
    for policy in policies:
        result = simulate(policy, p, signal=signal)
        rows.extend(result)
        summaries[policy] = metrics(result, p.target, p.dt)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    report = {'seed': seed, 'parameters': asdict(p), 'metrics': summaries}
    output.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    if plot:
        import matplotlib.pyplot as plt
        for policy in policies:
            subset = [r for r in rows if r['policy'] == policy]
            plt.plot([r['time'] for r in subset], [r['prey'] for r in subset], label=policy)
        plt.axhline(p.target, linestyle='--', label='prey target')
        plt.xlabel('Time')
        plt.ylabel('Normalized prey')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output.with_suffix('.png'), dpi=160)
        plt.close()
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/baseline.csv')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--disturbance', type=float, default=0.1)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.seed, args.disturbance, args.plot)['metrics'], indent=2))


if __name__ == '__main__':
    main()
