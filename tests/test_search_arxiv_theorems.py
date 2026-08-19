import unittest
from unittest.mock import patch

import search_arxiv_theorems as search_module


class SearchArxivTheoremsTests(unittest.TestCase):
    def test_auto_falls_back_to_matlas(self):
        matlas_results = [{"title": "Result", "provider": "matlas"}]
        with patch.object(search_module, "_search_leansearch", side_effect=TimeoutError("down")):
            with patch.object(search_module, "_search_matlas", return_value=matlas_results):
                result = search_module.search("test theorem", provider="auto")

        self.assertEqual(result["provider"], "matlas")
        self.assertEqual(result["results"], matlas_results)
        self.assertEqual(result["fallback_errors"][0]["provider"], "leansearch")

    def test_explicit_leansearch_does_not_fallback(self):
        with patch.object(search_module, "_search_leansearch", side_effect=TimeoutError("down")):
            with self.assertRaises(TimeoutError):
                search_module.search("test theorem", provider="leansearch")

    def test_matlas_clamps_request_but_slices_response(self):
        payload = [
            {"candidate_id": str(i), "title": f"T{i}", "statement": f"S{i}"}
            for i in range(10)
        ]
        with patch.object(search_module, "_post_json", return_value=payload) as post:
            results = search_module._search_matlas("query", num_results=3, timeout=9)

        self.assertEqual(len(results), 3)
        self.assertEqual(post.call_args.args[1]["num_results"], 10)
        self.assertEqual(post.call_args.kwargs["timeout"], 9)

    def test_rejects_invalid_arguments(self):
        for kwargs in (
            {"query": ""},
            {"query": "x", "num_results": 0},
            {"query": "x", "provider": "unknown"},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    search_module.search(**kwargs)


if __name__ == "__main__":
    unittest.main()
