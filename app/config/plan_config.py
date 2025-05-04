import json
import os

# 모델 경로 설정 파일
MODEL_CONFIG_FILE = os.getenv("MODEL_CONFIG_FILE", "config/models.json")

# 모델 경로를 설정 파일에서 로드하는 함수
def load_model_paths() -> dict:
    try:
        with open(MODEL_CONFIG_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Failed to load model paths from config file: {str(e)}")

# 모델 경로를 동적으로 로드
MODEL_PATHS = load_model_paths()

# 언어에 해당하는 모델 경로를 반환하는 함수
def get_model_for_language(lang: str) -> str:
    return MODEL_PATHS.get(lang, MODEL_PATHS["en"])  # 기본값으로 영어 모델을 반환
