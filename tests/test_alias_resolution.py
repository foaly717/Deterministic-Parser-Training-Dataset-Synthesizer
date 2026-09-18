from dataset_tools.evidence.index import EvidenceIndex
from dataset_tools.validators.options import validate_cli_response


def test_alias_option_is_accepted():
    # Populate EvidenceIndex with canonical flag and aliases
    valid_options = {"-help", "-h", "-?", "--help"}
    evidence_index = EvidenceIndex(valid_options=valid_options)

    ok_h, _ = validate_cli_response("ffmpeg -h", evidence_index)
    ok_help, _ = validate_cli_response("ffmpeg --help", evidence_index)
    ok_q, _ = validate_cli_response("ffmpeg -?", evidence_index)

    assert ok_h is True
    assert ok_help is True
    assert ok_q is True
