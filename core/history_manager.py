
import pandas as pd

from core.dataset import Dataset


class HistoryManager:
    """Manage dataset snapshots for undo and redo."""

    def __init__(self, max_states=50):
        self.max_states = max_states
        self.states = []
        self.current_index = -1

    def reset(self, dataset):
        """Start a fresh history when a spreadsheet is loaded."""

        self.states = [
            ("Loaded dataset", dataset.copy())
        ]
        self.current_index = 0

    def record(self, dataset, operation_name):
        """Record a new dataset state after an approved operation."""

        if dataset is None:
            return

        if self.current_index == -1:
            self.reset(dataset)
            return

        current_dataset = self.states[self.current_index][1]

        # Avoid recording an operation that changed nothing.
        if (
            current_dataset.dataframe.equals(dataset.dataframe)
            and current_dataset.columns == dataset.columns
        ):
            return

        # A new change after Undo discards the old Redo path.
        self.states = self.states[:self.current_index + 1]

        self.states.append((operation_name, dataset.copy()))
        self.current_index += 1

        # Keep the history within the configured limit.
        if len(self.states) > self.max_states:
            excess = len(self.states) - self.max_states
            self.states = self.states[excess:]
            self.current_index -= excess

    def can_undo(self):
        return self.current_index > 0

    def can_redo(self):
        return self.current_index < len(self.states) - 1

    def undo(self):
        """Move back one state and return a separate dataset copy."""

        if not self.can_undo():
            return None

        self.current_index -= 1
        return self.states[self.current_index][1].copy()

    def redo(self):
        """Move forward one state and return a separate dataset copy."""

        if not self.can_redo():
            return None

        self.current_index += 1
        return self.states[self.current_index][1].copy()

    def get_history(self):
        """Return a readable table of recorded states."""

        rows = []

        for index, (operation_name, dataset) in enumerate(self.states):
            if index == self.current_index:
                status = "Current"
            elif index < self.current_index:
                status = "Previous"
            else:
                status = "Available for Redo"

            rows.append({
                "Step": index,
                "Operation": operation_name,
                "Rows": dataset.row_count,
                "Columns": dataset.column_count,
                "Status": status
            })

        return pd.DataFrame(
            rows,
            columns=["Step", "Operation", "Rows", "Columns", "Status"]
        )
