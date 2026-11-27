import json

from aws_lambda.handler import lambda_handler


def test_health():
    r = lambda_handler({"routeKey": "GET /health"}, None)
    assert r["statusCode"] == 200


def test_predict_positive():
    event = {"routeKey": "POST /predict", "body": json.dumps({"text": "I love this"})}
    r = lambda_handler(event, None)
    assert r["statusCode"] == 200
    assert json.loads(r["body"])["label"] == "positive"


def test_predict_empty_text():
    event = {"routeKey": "POST /predict", "body": json.dumps({"text": "  "})}
    assert lambda_handler(event, None)["statusCode"] == 400