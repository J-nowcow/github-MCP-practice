"""유틸리티 함수 단위 테스트."""

import pytest
from mcp_github.utils import (
    is_text,
    summarize_diff,
    format_file_size,
    is_binary_file
)


class TestUtils:
    """유틸리티 함수 테스트 클래스."""

    def test_is_text_with_text_content(self):
        """텍스트 콘텐츠 감지 테스트."""
        text_content = b"Hello, World!\nThis is a text file."
        assert is_text(text_content) is True

    def test_is_text_with_binary_content(self):
        """바이너리 콘텐츠 감지 테스트."""
        binary_content = b"\x00\x01\x02\x03\xff\xfe\xfd"
        assert is_text(binary_content) is False

    def test_is_text_with_empty_content(self):
        """빈 콘텐츠 테스트."""
        empty_content = b""
        assert is_text(empty_content) is True

    def test_is_text_with_unicode_content(self):
        """유니코드 콘텐츠 테스트."""
        unicode_content = "안녕하세요, 세계!".encode('utf-8')
        assert is_text(unicode_content) is True

    def test_summarize_diff_with_small_diff(self):
        """작은 diff 요약 테스트."""
        diff_content = "@@ -1,1 +1,1 @@\n-old line\n+new line\n"
        summary = summarize_diff(diff_content, max_chars=50)
        assert len(summary) <= 50
        assert "old line" in summary
        assert "new line" in summary

    def test_summarize_diff_with_large_diff(self):
        """큰 diff 요약 테스트."""
        # 긴 diff 콘텐츠 생성
        long_diff = "@@ -1,1 +1,1 @@\n" + "-old line\n+new line\n" * 100
        summary = summarize_diff(long_diff, max_chars=100)
        assert len(summary) <= 100
        assert "..." in summary  # 트렁케이션 표시

    def test_summarize_diff_with_empty_diff(self):
        """빈 diff 요약 테스트."""
        empty_diff = ""
        summary = summarize_diff(empty_diff, max_chars=50)
        assert summary == ""

    def test_format_file_size_bytes(self):
        """바이트 단위 파일 크기 포맷팅 테스트."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1023) == "1023 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1025) == "1.0 KB"

    def test_format_file_size_kilobytes(self):
        """킬로바이트 단위 파일 크기 포맷팅 테스트."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        # TB 단위는 현재 구현에서 지원하지 않음
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1024.0 GB"

    def test_format_file_size_decimal_precision(self):
        """소수점 정밀도 테스트."""
        assert format_file_size(1500) == "1.5 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(1572) == "1.5 KB"

    def test_is_binary_file_with_text_extensions(self):
        """텍스트 파일 확장자 테스트."""
        assert is_binary_file("README.md") is False
        assert is_binary_file("script.py") is False
        assert is_binary_file("config.json") is False
        assert is_binary_file("style.css") is False
        assert is_binary_file("data.csv") is False

    def test_is_binary_file_with_binary_extensions(self):
        """바이너리 파일 확장자 테스트."""
        assert is_binary_file("image.png") is True
        assert is_binary_file("document.pdf") is True
        assert is_binary_file("archive.zip") is True
        assert is_binary_file("executable.exe") is True
        assert is_binary_file("library.so") is True

    def test_is_binary_file_with_no_extension(self):
        """확장자 없는 파일 테스트."""
        assert is_binary_file("Dockerfile") is False
        assert is_binary_file("Makefile") is False
        assert is_binary_file("LICENSE") is False

    def test_is_binary_file_case_insensitive(self):
        """대소문자 구분 없는 테스트."""
        assert is_binary_file("IMAGE.PNG") is True
        assert is_binary_file("readme.MD") is False
        assert is_binary_file("Script.PY") is False

    def test_edge_cases(self):
        """엣지 케이스 테스트."""
        # None 값
        with pytest.raises(AttributeError):
            is_binary_file(None)
        
        # 빈 문자열
        assert is_binary_file("") is False
        
        # 특수 문자 포함
        assert is_binary_file("file.with.dots.txt") is False
        assert is_binary_file("file-with-dashes.py") is False
        assert is_binary_file("file_with_underscores.json") is False
