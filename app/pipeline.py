"""Three-stage inference pipeline: preprocess -> infer -> postprocess.
The same functions are reused by AWS Lambda and Knative."""

# Toy "model": word weights. Positive score = positive sentiment.
WEIGHTS = {
    "good": 1.0, "great": 2.0, "love": 2.0, "excellent": 2.0, "happy": 1.5,
    "bad": -1.0, "terrible": -2.0, "hate": -2.0, "awful": -2.0, "sad": -1.5,
}


def preprocess(text: str) -> list[str]:
    """Stage 1: clean the input and split it into words."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    cleaned = "".join(c for c in text.lower() if c.isalnum() or c.isspace())
    return cleaned.split()


def infer(tokens: list[str]) -> float:
    """Stage 2: 'model' inference. Returns a sentiment score."""
    return sum(WEIGHTS.get(t, 0.0) for t in tokens)


def postprocess(score: float) -> dict:
    """Stage 3: turn the raw score into a response."""
    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"
    return {"label": label, "score": score}


def run_pipeline(text: str) -> dict:
    return postprocess(infer(preprocess(text)))