"""
Unit Tests for R Bridge and Type Marshaling
"""
import pytest
import pandas as pd
from causal_lab.bridge.r_bridge import RBridge
from causal_lab.bridge.schemas import EstimatorResult


def test_r_bridge_execution():
    bridge = RBridge()
    # Simple test dataset
    df = pd.DataFrame({
        "cluster_id": ["A", "A", "B", "B", "C", "C", "D", "D"] * 10,
        "treatment": [0, 1, 0, 1, 0, 1, 0, 1] * 10,
        "outcome": [1.0, 3.2, 1.5, 4.0, 0.8, 2.9, 1.2, 3.5] * 10
    })

    res = bridge.fit_mixed_effects(df, formula="outcome ~ treatment + (1 | cluster_id)")
    assert isinstance(res, EstimatorResult)
    assert res.n_obs == 80
    assert res.n_clusters == 4
    assert res.treatment_effect.estimate > 1.5
    assert res.icc is not None
