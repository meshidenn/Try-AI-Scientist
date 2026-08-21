"""旧workspace pathとの互換wrapper。実装本体はproject packageにある。"""

from pathlib import Path
import sys

_project_src = Path(__file__).resolve().parents[1] / "src"
if str(_project_src) not in sys.path:
    sys.path.insert(0, str(_project_src))

from pdf_to_markdown_toyota.interfaces.cli.evaluate_page_ngrams import *  # noqa: F401,F403
from pdf_to_markdown_toyota.interfaces.cli.evaluate_page_ngrams import main


if __name__ == "__main__":
    raise SystemExit(main())
