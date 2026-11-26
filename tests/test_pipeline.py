import pytest
from app.pipeline import preprocess, infer, postprocess, run_pipeline


def test_preprocess_cleans_text():
    assert preprocess("I LOVE this!") == ["i", "love", "this"]


def test_preprocess_rejects_empty():
    with pytest.raises(ValueError):
        preprocess("   ")


def test_infer_scores_words():
    assert infer(["great", "bad"]) == 1.0


def test_postprocess_labels():
    assert postprocess(2.0)["label"] == "positive"
    assert postprocess(-1.0)["label"] == "negative"
    assert postprocess(0.0)["label"] == "neutral"


def test_full_pipeline():
    assert run_pipeline("This is excellent, I love it")["label"] == "positive"