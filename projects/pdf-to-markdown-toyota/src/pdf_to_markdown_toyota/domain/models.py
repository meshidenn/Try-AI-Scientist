"""PDF変換projectのdomain modelと固定資料定義。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentSpec:
    """評価対象PDFの識別情報。"""

    key: str
    label: str
    filename: str
    url: str


DOCUMENTS = (
    DocumentSpec(
        "securities_report",
        "有価証券報告書",
        "securities-report-2026.pdf",
        "https://global.toyota/pages/global_toyota/ir/library/securities-report/archives/archives_2026_03.pdf",
    ),
    DocumentSpec(
        "earnings_presentation",
        "決算説明会資料",
        "earnings-presentation-2026.pdf",
        "https://global.toyota/pages/global_toyota/ir/financial-results/2026_4q_presentation_jp.pdf",
    ),
    DocumentSpec(
        "integrated_report",
        "統合報告書",
        "integrated-report-2025.pdf",
        "https://global.toyota/pages/global_toyota/ir/library/annual/2025_001_integrated_jp.pdf",
    ),
    DocumentSpec(
        "midterm_policy",
        "中期経営計画書相当資料（2030年電動化戦略）",
        "midterm-policy-2030-electrification.pdf",
        "https://global.toyota/en/filedownload/20399572",
    ),
)
