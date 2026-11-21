"""
Unit Tests for Hierarchical DGP and Scenarios
"""
import pytest
import numpy as np
from causal_lab.config import DGPConfig, RandomizationScheme
from causal_lab.simulation.generator import HierarchicalDGP
from causal_lab.simulation import scenarios


def test_dgp_generation_shape():
    cfg = DGPConfig(n_clusters=10, avg_cluster_size=20, cluster_size_dispersion=0.0, seed=42)
    dgp = HierarchicalDGP(cfg)
    df = dgp.generate()

    assert len(df) == 200
    assert set(df.columns) == {"unit_id", "cluster_id", "treatment", "pre_covariate", "cluster_effect", "outcome"}
    assert df["cluster_id"].nunique() == 10
    assert df["treatment"].isin([0, 1]).all()


def test_dgp_reproducibility():
    cfg = DGPConfig(seed=123)
    dgp1 = HierarchicalDGP(cfg)
    dgp2 = HierarchicalDGP(cfg)

    df1 = dgp1.generate()
    df2 = dgp2.generate()

    np.testing.assert_allclose(df1["outcome"].values, df2["outcome"].values)


def test_simpsons_reversal_scenario():
    cfg = scenarios.get_simpsons_reversal_scenario()
    dgp = HierarchicalDGP(cfg)
    df = dgp.generate()

    assert len(df) > 1000
    assert df["cluster_id"].nunique() == cfg.n_clusters
