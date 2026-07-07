from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.workflows.activities import (
        ingest_activity,
        analyze_activity,
        persist_findings_activity,
        mark_run_activity,
    )

_RETRY = RetryPolicy(maximum_attempts=3)


@workflow.defn
class DiligenceWorkflow:
    @workflow.run
    async def run(self, company_id: int, run_id: int) -> dict:
        try:
            await workflow.execute_activity(
                mark_run_activity, args=[run_id, "running"],
                start_to_close_timeout=timedelta(minutes=1),
            )
            await workflow.execute_activity(
                ingest_activity, args=[company_id],
                start_to_close_timeout=timedelta(minutes=10), retry_policy=_RETRY,
            )
            findings = await workflow.execute_activity(
                analyze_activity, args=[company_id, run_id],
                start_to_close_timeout=timedelta(minutes=10), retry_policy=_RETRY,
            )
            count = await workflow.execute_activity(
                persist_findings_activity, args=[run_id, company_id, findings],
                start_to_close_timeout=timedelta(minutes=2), retry_policy=_RETRY,
            )
            await workflow.execute_activity(
                mark_run_activity, args=[run_id, "completed"],
                start_to_close_timeout=timedelta(minutes=1),
            )
            return {"findings": count}
        except Exception:
            await workflow.execute_activity(
                mark_run_activity, args=[run_id, "failed"],
                start_to_close_timeout=timedelta(minutes=1),
            )
            raise