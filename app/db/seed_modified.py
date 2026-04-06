# app/db/seed.py
from sqlalchemy import select

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import role_permissions   # Table, not a class
from app.core.logging import get_logger

logger = get_logger()


ALL_PERMISSIONS: list[tuple[str, str]] = [
    ("financial_records", "read"),
    ("financial_records", "create"),
    ("financial_records", "update"),
    ("financial_records", "delete"),
    ("financial_records", "read_history"),
    ("analytics",         "read"),
    ("analytics",         "read_trends"),
    ("analytics",         "export"),
    ("categories",        "create"),
    ("categories",        "delete"),
    ("users",             "read_own"),
    ("users",             "list"),
    ("users",             "create"),
    ("users",             "update"),
    ("users",             "delete"),
    ("roles",             "list"),
    ("roles",             "manage"),
]

ROLE_PERMISSIONS: dict[str, list[tuple[str, str]]] = {
    "viewer": [
        ("financial_records", "read"),
        ("analytics",         "read"),
        ("users",             "read_own"),
    ],
    "analyst": [
        ("financial_records", "read"),
        ("financial_records", "read_history"),
        ("analytics",         "read"),
        ("analytics",         "read_trends"),
        ("analytics",         "export"),
        ("users",             "read_own"),
    ],
    "admin": [
        ("financial_records", "read"),
        ("financial_records", "create"),
        ("financial_records", "update"),
        ("financial_records", "delete"),
        ("financial_records", "read_history"),
        ("analytics",         "read"),
        ("analytics",         "read_trends"),
        ("analytics",         "export"),
        ("categories",        "create"),
        ("categories",        "delete"),
        ("users",             "read_own"),
        ("users",             "list"),
        ("users",             "create"),
        ("users",             "update"),
        ("users",             "delete"),
        ("roles",             "list"),
        ("roles",             "manage"),
    ],
}


async def seed_roles_and_permissions(db) -> None:
    logger.info("seeding roles and permissions")

    # ── Step 1: upsert all permissions ────────────────────────────────────────
    permissions_map: dict[tuple[str, str], Permission] = {}

    for resource, action in ALL_PERMISSIONS:
        result = await db.execute(
            select(Permission).where(
                Permission.resource == resource,
                Permission.action   == action,
            )
        )
        perm = result.scalar_one_or_none()

        if not perm:
            perm = Permission(resource=resource, action=action)
            db.add(perm)
            await db.flush()
            logger.info("created permission", extra={"resource": resource, "action": action})

        permissions_map[(resource, action)] = perm

    # ── Step 2: upsert all roles ──────────────────────────────────────────────
    for role_name, granted_perms in ROLE_PERMISSIONS.items():
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalar_one_or_none()

        if not role:
            role = Role(name=role_name)
            db.add(role)
            await db.flush()
            logger.info("created role", extra={"role": role_name})

        # ── Step 3: upsert role → permission assignments ──────────────────────
        for resource, action in granted_perms:
            perm = permissions_map.get((resource, action))

            if perm is None:
                raise ValueError(
                    f"Role '{role_name}' references undeclared permission "
                    f"'{resource}:{action}'. Add it to ALL_PERMISSIONS first."
                )

            # Table.c accessor — correct way to query a plain Table object
            result = await db.execute(
                select(role_permissions).where(
                    role_permissions.c.role_id       == role.id,
                    role_permissions.c.permission_id == perm.id,
                )
            )
            exists = result.fetchone()

            if not exists:
                await db.execute(
                    role_permissions.insert().values(
                        role_id=role.id,
                        permission_id=perm.id,
                    )
                )
                logger.info(
                    "assigned permission to role",
                    extra={"role": role_name, "resource": resource, "action": action},
                )

    await db.commit()
    logger.info("seed complete")