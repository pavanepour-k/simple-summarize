import json
import os


class PlanConfigService:
    def __init__(self):
        self.model_paths = self._load_model_paths()

    def _load_model_paths(self) -> dict:
        # Load model paths from configuration file
        try:
            # Use environment variables to set path
            config_path = os.getenv("MODEL_CONFIG_PATH", "config/models.json")
            with open(config_path, "r") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load model paths from config file: {str(e)}")

    def get_model_for_language(self, lang: str) -> str:
        # Return model path for the specified language
        return self.model_paths.get(
            lang, self.model_paths["en"]
        )  # Default to English model

    def get_time_based_limit(self, role: str, plan: str, hour: int) -> int:
        # Get time-based API call limit
        time_limits = {
            "user": {
                0: 50,
                6: 200,
                12: 300,
                18: 150,
            },
            "pro": {
                0: 100,
                6: 500,
                12: 1000,
                18: 800,
            },
        }
        role = role.lower()
        plan = plan.lower()
        return time_limits.get(role, {}).get(hour, 100)  # Default to 100 calls
