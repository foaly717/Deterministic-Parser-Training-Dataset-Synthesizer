from dataset_tools.evidence.loaders.cli_help import CLIHelpLoader
from dataset_tools.evidence.loaders.ffmpeg import FFmpegLoader
from dataset_tools.evidence.loaders.manpage import ManPageLoader
from dataset_tools.evidence.loaders.markdown import MarkdownEvidenceLoader


LOADERS = [
    CLIHelpLoader(
        tool_name="HandBrakeCLI",
        filename="handbrakecli-help.txt",
    ),
    FFmpegLoader(),
    CLIHelpLoader(),
    MarkdownEvidenceLoader(),
    ManPageLoader(),
]


def load_evidence(path):
    for loader in LOADERS:
        if loader.supports(path):
            return loader.load(path)

    raise ValueError(f"No evidence loader available for: {path}")
