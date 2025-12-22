import re
from dataclasses import dataclass
from typing import List

from src.models.diffhunk import DiffHunk

class DiffParser:
    def __init__(self):
        # diff --git a/(SOURCE) b/(TARGET) -> Captures filename
        self.file_header_pattern = re.compile(r"diff --git a/.* b/(.*)")
        
        # @@ -OLD_START,OLD_COUNT +NEW_START,NEW_COUNT @@
        # We only capture the NEW_START (\d+)
        self.hunk_header_pattern = re.compile(r"@@ \-\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

    def parse(self, diff_text: str) -> List[DiffHunk]:
        hunks = []
        current_file = None
        current_hunk_lines = []
        current_start_line = 0
        
        # Tracker for the line number in the NEW file
        active_line_number = 0

        def flush_hunk():
            # Helper to save the hunk state and reset
            nonlocal current_hunk_lines
            if current_file and current_hunk_lines:
                hunks.append(DiffHunk(
                    file_path=current_file,
                    start_line=current_start_line,
                    changed_lines=current_hunk_lines
                ))
                current_hunk_lines = []

        lines = diff_text.splitlines()

        for line in lines:
            file_match = self.file_header_pattern.match(line)
            if file_match:
                flush_hunk()
                current_file = file_match.group(1)
                active_line_number = 0
                continue

            # Hunk Header (@@ ... @@)
            hunk_match = self.hunk_header_pattern.match(line)
            if hunk_match:
                flush_hunk()

                if current_file and current_hunk_lines:
                    hunks.append(DiffHunk(current_file, current_start_line, current_hunk_lines))
                
                # Start of new hunk
                current_start_line = int(hunk_match.group(1))
                active_line_number = current_start_line
                continue

            # Content Lines
            if current_file and active_line_number > 0:
                if line.startswith("+++"):
                    continue
                
                if line.startswith("+"):
                    current_hunk_lines.append(active_line_number)
                    active_line_number += 1
                
                if line.startswith(" "):
                    active_line_number += 1

                # Deleted lines dont advance the line counter
        flush_hunk()
        return hunks