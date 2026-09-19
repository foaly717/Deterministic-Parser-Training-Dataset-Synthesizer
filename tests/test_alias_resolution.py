from dataset_tools.validators.options import validate_cli_response


def test_alias_option_is_accepted():
    valid_options = frozenset({
        "-help",
        "-h",
        "-?",
        "--help",
    })

    ok_h, _ = validate_cli_response(
        "ffmpeg -h",
        valid_options,
    )
    ok_help, _ = validate_cli_response(
        "ffmpeg --help",
        valid_options,
    )
    ok_q, _ = validate_cli_response(
        "ffmpeg -?",
        valid_options,
    )

    assert ok_h is True
    assert ok_help is True
    assert ok_q is True
