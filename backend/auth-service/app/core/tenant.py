from contextvars import ContextVar, Token

# =========================
# CONTEXTO GLOBAL DO TENANT
# =========================
tenant_id_context: ContextVar[int | None] = ContextVar(
    "tenant_id",
    default=None
)

# guarda token para rollback seguro
tenant_token_context: ContextVar[Token | None] = ContextVar(
    "tenant_token",
    default=None
)


# =========================
# SET TENANT (SEGURO)
# =========================
def set_tenant_id(company_id: int) -> None:
    token = tenant_id_context.set(company_id)
    tenant_token_context.set(token)


# =========================
# GET TENANT (SEGURO)
# =========================
def get_tenant_id() -> int | None:
    return tenant_id_context.get()


# =========================
# RESET SEGURO (ROLLBACK CONTEXT)
# =========================
def clear_tenant_id() -> None:
    token = tenant_token_context.get()

    if token:
        tenant_id_context.reset(token)
        tenant_token_context.set(None)