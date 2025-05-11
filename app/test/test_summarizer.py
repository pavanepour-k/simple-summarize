import unittest
from app.services.summarizer import Summarizer
from app.services.model_loader import model_loader

class TestSummarizer(unittest.TestCase):

    def setUp(self):
        """테스트 시작 전에 실행되는 설정 함수"""
        self.summarizer = Summarizer(model_loader)

    def test_summarize_text_success(self):
        """정상적인 텍스트 요약을 테스트"""
        text = "The quick brown fox jumps over the lazy dog"
        result = self.summarizer.summarize(text)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_summarize_text_empty(self):
        """빈 텍스트에 대한 요약을 테스트"""
        text = ""
        result = self.summarizer.summarize(text)
        self.assertEqual(result, "No text to summarize")
    
    def test_summarizer_invalid_model(self):
        """잘못된 모델 설정에 대한 테스트"""
        model_loader.get_pipeline("invalid_lang")
        with self.assertRaises(Exception):
            self.summarizer.summarize("Invalid model test")
    
    def test_summarizer_large_text(self):
        """너무 긴 텍스트에 대한 요약을 테스트 (경계값 테스트)"""
        long_text = " ".join(["Lorem ipsum dolor sit amet"] * 1000)  # 1000번 반복된 텍스트
        result = self.summarizer.summarize(long_text)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
if __name__ == '__main__':
    unittest.main()
