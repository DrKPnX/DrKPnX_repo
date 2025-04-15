from log_analyzer import (
    split_and_clear,
    get_config,
    replace_path,
    open_log,
)
import json
import gzip


def test_split_and_clear():
    test_line = (
        '1.2.3.4 - - [01/Jan/2023:12:34:56 +0000] "GET /api/v1/test HTTP/1.1" 200 1234 "-" '
        '"python-requests/2.28.1" "-" "-" "-" 0.123'
    )
    expected = [
        '1.2.3.4',
        '-',
        '-',
        '01/Jan/2023:12:34:56 +0000',
        'GET /api/v1/test HTTP/1.1',
        '200',
        '1234',
        '-',
        'python-requests/2.28.1',
        '-',
        '-',
        '-',
        '0.123',
    ]
    assert split_and_clear(test_line) == expected


def test_get_config(tmp_path):
    # Создаём временный конфиг
    config_path = tmp_path / "config.json"
    config_data = {"REPORT_SIZE": 500, "LOG_DIR": "/tmp/logs"}
    with open(config_path, "w") as f:
        json.dump(config_data, f)

    # Тестируем загрузку
    class Args:
        config = str(config_path)

    config = get_config(Args())
    assert config["REPORT_SIZE"] == 500
    assert config["LOG_DIR"] == "/tmp/logs"
    assert config["REPORT_DIR"] == "./reports"  # значение по умолчанию



def test_open_log_gzip(tmp_path, monkeypatch):
    test_data = "line1\nline2\n"
    log_file = tmp_path / "nginx-access-ui.log-20230101.gz"
    with gzip.open(log_file, 'wt') as f:
        f.write(test_data)

    config = {"LOG_DIR": str(tmp_path)}
    data, date = next(open_log(config, "nginx-access-ui.log-20230101.gz"))
    assert data == ["line1", "line2", ""]
    assert date == "20230101"


def test_empty_line_handling():
    line = ""
    result = split_and_clear(line)
    assert result == [""]
