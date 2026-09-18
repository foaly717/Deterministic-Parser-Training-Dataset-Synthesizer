from pathlib import Path
from dataset_tools.evidence.loaders.ffmpeg import FFmpegLoader


def test_ffmpeg_loader_parses_help_text(tmp_path: Path):
    help_text = """
 -h <arg>          print help
 -y                overwrite output files
 -b:a bit_rate     set audio bitrate
"""
    file_path = tmp_path / "ffmpeg-help.txt"
    file_path.write_text(help_text, encoding="utf-8")

    loader = FFmpegLoader()
    assert loader.supports(file_path) is True

    doc = loader.load(file_path)
    values = {f.value for f in doc.facts}

    assert "-h" in values
    assert "-y" in values
    assert "-b:a" in values
