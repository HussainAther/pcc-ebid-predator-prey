from dataclasses import replace
import pytest
from pcc_predator_prey.simulation import Params, disturbances, simulate, policy_action, metrics
from pcc_predator_prey.experiment import run


def test_seed_reproducible():
    p = replace(Params(), steps=30)
    assert simulate(p=p, seed=9) == simulate(p=p, seed=9)


def test_policies_share_environment():
    p = replace(Params(), steps=30)
    s = disturbances(p, 9)
    a = simulate('none', p, signal=s)
    b = simulate('pcc_adaptive', p, signal=s)
    assert [r['disturbance'] for r in a] == [r['disturbance'] for r in b]


def test_nonnegative_and_bounded():
    a = simulate(p=replace(Params(), steps=100))
    assert all(r['prey'] >= 0 and r['predator'] >= 0 and 0 <= r['intervention'] <= .25 for r in a)


def test_pressure_proxy():
    act, pressure, proxy = policy_action('pcc_adaptive', .2, .5, [0, .1, -.1])
    assert pressure == pytest.approx(.6)
    assert 0 <= proxy <= 1
    assert 0 <= act <= .25


def test_invalid_params():
    with pytest.raises(ValueError):
        simulate(p=replace(Params(), dt=0))
    with pytest.raises(ValueError):
        simulate(p=replace(Params(), steps=4), signal=[0])


def test_output(tmp_path):
    output = tmp_path / 'run.csv'
    result = run(output)
    assert output.exists() and output.with_suffix('.json').exists()
    assert set(result['metrics']) == {'none', 'fixed', 'pcc_adaptive'}
    assert metrics(simulate('none', replace(Params(), steps=3)), .55, .02)['cumulative_intervention'] == 0
