import tempfile
import unittest
from pathlib import Path

from category_grounded_agentic_search.application.derived_artifacts import DerivedArtifactPaths


class DerivedArtifactPathsTest(unittest.TestCase):
    def test_separates_stages_and_models(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            paths = DerivedArtifactPaths(
                root=Path(temporary_directory),
                corpus_id="UltraDomain",
                corpus_revision="abc123",
                extractor_model="Qwen/Qwen3.6-35B",
                embedding_model="BAAI/bge-m3",
            )
            paths.initialize()
            manifest = paths.write_manifest("triplets", inputs={"source": "mix.jsonl"}, outputs={})

            self.assertTrue(manifest.is_file())
            self.assertIn("Qwen--Qwen3.6-35B", str(paths.triplet_dir))
            self.assertIn("BAAI--bge-m3", str(paths.embedding_dir))
            self.assertNotEqual(paths.triplet_dir, paths.embedding_dir)
