from transformers import pipeline
from app.models.request_model import SummaryOption
from functools import lru_cache
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# 모델 캐싱 (한 번만 로드하고 재사용)
@lru_cache()
def get_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

# 요약 길이 매핑
length_mapping = {
    SummaryOption.short: 60,
    SummaryOption.medium: 120,
    SummaryOption.long: 200,
}

def summarize_text(content: str, option: SummaryOption) -> dict:
    summarizer = get_summarizer()
    max_len = length_mapping[option]
    result = summarizer(content, max_length=max_len, min_length=20, do_sample=False)
    summary = result[0]['summary_text']

    # 언어 자동 감지 (짧은 텍스트 오류 방지)
    try:
        language = detect(content)
    except LangDetectException:
        language = "en"

    return {
        "summary": summary,
        "length": option.value,
        "input_length": len(content),
        "language": language
    }
