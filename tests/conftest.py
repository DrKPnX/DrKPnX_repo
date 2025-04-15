import pytest
import tempfile
import os

@pytest.fixture
def sample_log_file():
    log_content = """1.2.3.4 - - [01/Jan/2023:12:34:56 +0000] "GET /api/v1/test HTTP/1.1" 200 1234 "-" "python-requests/2.28.1" "-" "-" "-" 0.123"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(log_content)
    yield f.name
    os.unlink(f.name)