import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.config import settings
from app.workflows.activities import analyze_activity, ingest_activity, mark_run_activity, persist_findings_activity
from app.workflows.diligence_workflow import DiligenceWorkflow


async def main() -> None:
    client = await Client.connect(settings.temporal_address)
    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[DiligenceWorkflow],
        activities=[ingest_activity, analyze_activity, persist_findings_activity, mark_run_activity],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
