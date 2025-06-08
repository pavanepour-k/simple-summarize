import logging
import os
from pathlib import Path
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

logger = logging.getLogger(__name__)


def load_model(model_name: str):
    try:
        # Check for local directory
        if os.path.isdir(model_name):
            model_path = Path(model_name)
            # Basic integrity check for common files
            if not (model_path / "config.json").exists():
                raise FileNotFoundError(f"config.json not found in {model_path}")
        else:
            model_path = model_name

        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Ensure the weights are loaded
        if not hasattr(model, "state_dict"):
            raise ValueError("Model checkpoint is missing state_dict")

        return pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
        )

    except Exception as exc:
        logger.error("Failed to load model %s: %s", model_name, exc)
        raise