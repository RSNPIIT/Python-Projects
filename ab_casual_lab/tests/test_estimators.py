"""
Unit Tests for Causal Estimators
"""
import pytest
import numpy as np
from causal_lab.config import DGPConfig
from causal_lab.simulation.generator import HierarchicalDGP
from causal_lab.estimators.naive_ols import NaiveOLSEstimator
from causal_lab.estimators.cluster_robust_ols import ClusterRobustOLSEstimator
from causal_lab.estimators.mixed_effects import MixedEffectsEstimator
from causal_lab.estimators.cuped_cluster import CUPEDMixedEffectsEstimator
from causal_lab.bridge.r_bridge import RBridge


@pytest.fixture(scope="module")
def sample_data():
    cfg = DGPConfig(n_clusters=20, avg_cluster_size=30, true_tau=2.0, icc=0.25, seed=99)
    dgp = HierarchicalDGP(cfg)
    return dgp.generate()


@pytest.fixture(scope="module")
def r_bridge():
    return RBridge()


def test_naive_ols(sample_data):
    est = NaiveOLSEstimator()
    res = est.fit(sample_data)

    te = res.treatment_effect
    assert np.isfinite(te.estimate)
    assert te.std_error > 0.0
    assert 0.0 <= te.p_value <= 1.0
    assert te.ci_lower < te.ci_upper


def test_cluster_robust_ols(sample_data):
    est = ClusterRobustOLSEstimator()
    res = est.fit(sample_data)

    te = res.treatment_effect
    assert np.isfinite(te.estimate)
    assert te.std_error > 0.0
    assert res.n_clusters == 20


def test_mixed_effects(sample_data, r_bridge):
    est = MixedEffectsEstimator(bridge=r_bridge)
    res = est.fit(sample_data)

    te = res.treatment_effect
    assert np.isfinite(te.estimate)
    assert te.std_error > 0.0
    assert res.icc is not None
    assert 0.0 <= res.icc <= 1.0
    assert res.sigma_cluster is not None and res.sigma_cluster > 0.0


def test_cuped_mixed_effects(sample_data, r_bridge):
    est = CUPEDMixedEffectsEstimator(bridge=r_bridge)
    res = est.fit(sample_data)

    te = res.treatment_effect
    assert np.isfinite(te.estimate)
    assert "cuped_theta" in res.diagnostics
