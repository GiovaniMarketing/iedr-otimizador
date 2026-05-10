from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.core.tenant import get_tenant_id


def apply_tenant_filter(session: Session):

    @event.listens_for(session, "do_orm_execute")
    def _add_tenant_filter(execute_state):

        if not execute_state.is_select:
            return

        statement = execute_state.statement

        # evita duplicar filtro
        if hasattr(statement, "_tenant_applied"):
            return

        tenant_id = get_tenant_id()

        # aplica filtro global
        statement = statement.where(
            statement.column_descriptions[0]["type"].company_id == tenant_id
        )

        statement._tenant_applied = True
        execute_state.statement = statement