from transformers import pipeline
from app.models.request_model import SummaryOption, SummaryStyle
from functools import lru_cache
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# 모델 캐싱 (한 번만 로드하고 재사용)
@lru_cache()
def get_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

def detect_language(text: str) -> str:
    """
    텍스트의 언어를 감지하여 ISO 코드 반환.
    감지 실패 시 'unknown' 반환.
    """
    try:
        return detect(text)
    except Exception:
        return "unknown"

def language_routing(text: str, lang: str) -> str:
    """
    감지된 언어에 따라 프롬프트 전처리를 수행.
    ko → 한국어, ja → 일본어, 그 외 → 원문 그대로.
    """
    if lang == "ko":
        return "아래 한국어 문서를 요약해주세요:\n" + text
    elif lang == "ja":
        return "以下の日本語コンテンツを要約してください:\n" + text
    else:
        return text

# 요약 길이 매핑
length_mapping = {
    SummaryOption.short: 60,
    SummaryOption.medium: 120,
    SummaryOption.long: 200,
}

def summarize_text(
    content: str,
    option: SummaryOption,
    style: SummaryStyle = SummaryStyle.general
) -> dict:
    """
    1) 언어 감지 및 라우팅
    2) 스타일 분기 처리
    3) 요약 모델 실행
    4) 결과 및 메타데이터 반환
    """
    # 1) 언어 감지 및 라우팅
    lang = detect_language(content)
    content = language_routing(content, lang)

    # 2) 스타일 분기 처리
    if style == SummaryStyle.problem_solver:
        content = (
            "Please summarize this content by focusing on identifying problems "
            "and their solutions:\n" + content
        )
    elif style == SummaryStyle.emotion_focused:
        content = (
            "Summarize the emotional or opinionated aspects of the following content:\n"
            + content
        )
    # general 스타일은 별도 처리 없음

    # 3) 요약 모델 실행
    summarizer = get_summarizer()
    max_len = length_mapping[option]
    result = summarizer(
        content,
        max_length=max_len,
        min_length=20,
        do_sample=False
    )
    summary = result[0].get("summary_text") or result[0].get("generated_text", "")

    # 4) 결과 반환
    return {
        "summary": summary,
        "length": option.value,
        "input_length": len(content),
        "language": lang,
        "style": style.value
    }
