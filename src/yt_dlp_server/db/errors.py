from yt_dlp_server.db.models import Task, TaskRecord


class TaskClaimError(Exception):
    """Exception raised when a task is claimed by another worker."""

    def __init__(self, task: Task, task_record: TaskRecord):
        self.task = task
        self.task_record = task_record

    def __str__(self):
        return (f"Task {self.task.job_id} / {self.task.url} has been claimed by {self.task_record.claimed_by} since "
                f"{self.task_record.claimed_at}, and timeout has not expired.")


class TaskNotFoundError(Exception):
    """Exception raised when a task is not found."""

    def __init__(self, task: Task):
        self.task = task
        self.message = f"Task not found: {task}"
        super().__init__(self.message)
