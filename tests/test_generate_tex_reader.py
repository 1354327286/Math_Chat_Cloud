import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_tex_reader import ReaderConverter, locate_reference, sha256


class GenerateTexReaderTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.project = Path(self.tempdir.name) / "problem"
        self.notes = self.project / "notes"
        self.refs = self.project / "refs"
        source_dir = self.refs / "sources" / "paper"
        source_dir.mkdir(parents=True)
        self.notes.mkdir()
        self.reference = source_dir / "main.tex"
        self.reference.write_text(
            """\\newtheorem{theorem}{Theorem}[section]
\\newtheorem{definition}[theorem]{Definition}
\\begin{document}
\\section{Setup}
\\begin{definition}\\label{def:test}
Test definition.
\\end{definition}
\\end{document}
""",
            encoding="utf-8",
        )
        (self.refs / "catalog.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "references": [
                        {
                            "id": "test",
                            "title": "Test paper",
                            "authors": ["A. Author"],
                            "arxiv_id": "2601.00001",
                            "source_url": "https://arxiv.org/abs/2601.00001v1",
                            "tex_main": "sources/paper/main.tex",
                            "txt_fallback": None,
                            "pdf": None,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.source = self.notes / "proof.tex"
        self.source.write_text(
            """\\documentclass{article}
\\title{Closed result}
\\author{}
\\begin{document}
\\maketitle
\\section{Statement}
See \\cite[Definition~1.1]{Ref}.
\\begin{theorem}[Test theorem]
\\label{thm:main}
The conclusion holds.
\\end{theorem}
\\begin{thebibliography}{9}
\\bibitem{Ref} A. Author, \\emph{Test paper}, arXiv:2601.00001v1,
\\url{https://arxiv.org/abs/2601.00001v1}.
\\end{thebibliography}
\\end{document}
""",
            encoding="utf-8",
        )
        self.output = self.notes / "proof.reader.md"

    def tearDown(self):
        self.tempdir.cleanup()

    def test_generates_derived_reader_without_changing_tex(self):
        before = self.source.read_bytes()
        rendered = ReaderConverter(self.source, self.output, self.project).convert()
        self.assertEqual(self.source.read_bytes(), before)
        self.assertIn(f"source-sha256: {sha256(self.source)}", rendered)
        self.assertIn("do-not-edit: true", rendered)
        self.assertIn("../refs/sources/paper/main.tex#L5-L7", rendered)
        self.assertIn("[public source](https://arxiv.org/abs/2601.00001v1)", rendered)

    def test_finds_numbered_reference_environment(self):
        self.assertEqual(locate_reference(self.reference, "Definition~1.1"), "L5-L7")


if __name__ == "__main__":
    unittest.main()
