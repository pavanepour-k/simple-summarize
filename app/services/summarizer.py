from app.models.response_model import SummaryOutput

def summarize_text(
    content: str,
    option: SummaryOption,
    style: SummaryStyle = SummaryStyle.general,
    lang: str = None
) -> SummaryOutput:
    # 언어 감지 없으면 기본값으로 감지
    if not lang:
        lang = detect_language(content)

    # 내용 라우팅
    routed = language_routing(content, lang)
    
    # 스타일에 맞는 프롬프트 설정
    style_prompt = ""
    if style == SummaryStyle.problem_solver:
        style_prompt = "Please summarize this content by focusing on identifying problems and their solutions:\n"
        routed = style_prompt + routed
    elif style == SummaryStyle.emotion_focused:
        style_prompt = "Summarize the emotional or opinionated aspects of the following content:\n"
        routed = style_prompt + routed

    # 언어 모델 선택 및 요약 생성
    summarizer = get_model_for_language(lang)
    max_len = length_mapping[option]

    result = summarizer(routed, max_length=max_len, min_length=20, do_sample=False)
    
    # 요약 텍스트 추출
    summary_text = result[0].get("summary_text") or result[0].get("generated_text", "")

    # 결과 반환 (style_prompt 필드 추가)
    return SummaryOutput(
        summary=summary_text,
        length=option.value,
        input_length=len(content),
        language=lang,
        style=style.value,
        style_prompt=style_prompt  # 추가된 필드
    )
