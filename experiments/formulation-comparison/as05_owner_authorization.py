"""Autorização auditável apenas para triagem exploratória; não é revisão independente."""
from __future__ import annotations

from as05_protocol import plan_digest


def verify_owner_authorization(authorization: dict, plan: dict) -> None:
    if not isinstance(authorization, dict):
        raise RuntimeError('AS05_OWNER_BLOCKED: documento malformado')
    expected = {
        'schema': 'AS05-OWNER-AUTHORIZATION-v1',
        'authorization_type': 'OWNER_APPROVED_EXPLORATORY',
        'authorized_by_owner': True,
        'scope': 'AS05_DEVELOPMENT_LP_ONLY',
        'independent_review_claimed': False,
        'plan_sha256': plan_digest(plan),
    }
    for field, value in expected.items():
        if authorization.get(field) != value:
            raise RuntimeError(f'AS05_OWNER_BLOCKED: {field} ausente ou divergente')
    if not isinstance(authorization.get('basis'), str) or not authorization['basis'].strip():
        raise RuntimeError('AS05_OWNER_BLOCKED: fundamentacao da autorizacao ausente')
