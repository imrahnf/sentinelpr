import unittest
from src.git.diff_parser import DiffParser

class TestDiffParser(unittest.TestCase):
    def test_parse_simple_hunk(self):
        diff_sample = """diff --git a/src/main.py b/src/main.py
index 83a..92b 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,3 +10,4 @@ def calculate_total(price):
     tax = 0.05
-    total = price * tax
+    total = price * (1 + tax)
+    print(f"Total: {total}")
     return total
"""
        parser = DiffParser()
        hunks = parser.parse(diff_sample)

        self.assertEqual(len(hunks), 1)
        self.assertEqual(hunks[0].file_path, "src/main.py")
        self.assertEqual(hunks[0].start_line, 10)
        self.assertEqual(hunks[0].changed_lines, [11, 12])

if __name__ == '__main__':
    unittest.main()