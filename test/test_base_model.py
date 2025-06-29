import pytest
from app.services.base_model import BaseEmbeddingModel


class TestBaseModel:
    def test_abstract_methods(self):
        with pytest.raises(TypeError):
            BaseEmbeddingModel()
    
    def test_interface_definition(self):
        class ConcreteModel(BaseEmbeddingModel):
            def load(self, model_path, **kwargs):
                pass
            
            def summarize(self, text, max_length, min_length, **kwargs):
                return [{"summary_text": "test"}]
            
            def get_info(self):
                return {"type": "concrete"}
        
        model = ConcreteModel()
        assert model.load("path") is None
        assert model.summarize("text", 100, 50) == [{"summary_text": "test"}]
        assert model.get_info() == {"type": "concrete"}