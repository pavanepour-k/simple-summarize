import unittest
from app.services.file_parser import validate_file_size, validate_file_type
from app.utils.error_handler import raise_http_exception

class TestFileSizeLimit(unittest.TestCase):
    
    def test_validate_file_size_within_limit(self):
        """파일 크기가 제한 내일 경우를 테스트"""
        file_size = 10 * 1024 * 1024  # 10MB (경계값)
        try:
            validate_file_size(file_size)
        except Exception as e:
            self.fail(f"validate_file_size raised {str(e)} unexpectedly!")

    def test_validate_file_size_exceeds_limit(self):
        """파일 크기가 제한을 초과할 경우를 테스트"""
        file_size = 10.1 * 1024 * 1024  # 10.1MB (초과)
        with self.assertRaises(Exception) as context:
            validate_file_size(file_size)
        
        self.assertEqual(str(context.exception), "File size exceeds the maximum limit of 10 MB")
    
    def test_validate_file_type_supported(self):
        """지원되는 파일 형식 검증"""
        try:
            validate_file_type("document.pdf")
        except Exception as e:
            self.fail(f"validate_file_type raised {str(e)} unexpectedly!")
    
    def test_validate_file_type_unsupported(self):
        """지원되지 않는 파일 형식 검증"""
        with self.assertRaises(Exception) as context:
            validate_file_type("document.exe")
        
        self.assertEqual(str(context.exception), "Unsupported file type. Allowed formats: .pdf, .docx, .txt, .md")
        
if __name__ == '__main__':
    unittest.main()
