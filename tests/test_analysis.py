import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import analyze_ceac as analysis


class AnalysisTests(unittest.TestCase):
    def load_rows(self, rows, delimiter=","):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "input").mkdir()
            text = "region,caseNumberFull,status,submitDate,Issued\n" + rows
            (root / "input/FY2024-ceac-current.csv").write_text(text.replace(",", delimiter), encoding="utf-8")
            with patch.object(analysis, "ROOT", root):
                return analysis.load(2024)

    def test_mixed_family_outcome_and_missing_date(self):
        d = self.load_rows("EU,2024EU1,Refused,2022-Oct-05,1\nEU,2024EU2,NVC,None,0\nEU,2024EU3,Issued,2022-Oct-06,2\n")
        g = analysis.aggregate(d[d.observed & d.date.notna()], ["year"])
        self.assertEqual(int(g.cases.iloc[0]), 2)
        self.assertEqual(int(g.issued_cases.iloc[0]), 2)
        self.assertEqual(int(g.principal_issued.iloc[0]), 1)
        self.assertEqual(int(g.visas.iloc[0]), 3)
        self.assertTrue(d.date.iloc[1] is not None and d.date.isna().iloc[1])

    def test_legacy_delimiter(self):
        d = self.load_rows("EU,2024EU1,Issued,05-Oct-2022,1\n", ";")
        self.assertEqual(str(d.date.iloc[0].date()), "2022-10-05")

    def test_invalid_date_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unparsed dates"):
            self.load_rows("EU,2024EU1,Issued,not-a-date,1\n")

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.load_rows("EU,2024EU1,Issued,2022-Oct-05,1\nEU,2024EU1,Issued,2022-Oct-05,1\n")


if __name__ == "__main__":
    unittest.main()
