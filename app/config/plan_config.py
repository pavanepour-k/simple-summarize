import json
import os

class PlanConfigService:
    def __init__(self):
        self.model_paths = self._load_model_paths()

    def _load_model_paths(self) -> dict:
        """모델 경로를 설정 파일에서 로드하는 함수"""
        try:
            with open("config/models.json", 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load model paths from config file: {str(e)}")

    def get_model_for_language(self, lang: str) -> str:
        """언어에 해당하는 모델 경로를 반환"""
        return self.model_paths.get(lang, self.model_paths["en"])  # 기본값으로 영어 모델을 반환

    def get_time_based_limit(self, role: str, plan: str, hour: int) -> int:
        """시간대에 따른 API 호출 제한"""
        time_limits = {
            "user": {
                0: 50, 6: 200, 12: 300, 18: 150,
            },
            "pro": {
                0: 100, 6: 500, 12: 1000, 18: 800,
            }
        }
        role = role.lower()
        plan = plan.lower()
        return time_limits.get(role, {}).get(hour, 100)  # 기본값 100개 제한
