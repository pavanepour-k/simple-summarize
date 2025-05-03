PLAN_RATE_LIMIT = {
    "user": 1000,
    "pro": 10000,
    "admin": 100000
}

def get_plan_limit(role: str) -> int:
    return PLAN_RATE_LIMIT.get(role.lower(), PLAN_RATE_LIMIT["user"])

LANGUAGE_MODELS = {
    "en": "facebook/bart-large-cnn",
    "ko": "Helsinki-NLP/opus-mt-ko-en",
    "ja": "sonoisa/t5-base-japanese-summarization"
}
