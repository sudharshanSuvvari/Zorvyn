# # app/db/seed.py

# from sqlalchemy import select

# from app.models.role import Role
# from app.models.permission import Permission
# from app.models.role_permission import role_permission


# async def seed_roles_permissions(db):

#     #  Define permissions
#     permissions_data = [
#         {"resource": "financial_records", "action": "read"},
#         {"resource": "financial_records", "action": "create"},
#         {"resource": "financial_records", "action": "update"},
#         {"resource": "financial_records", "action": "delete"},
#         {"resource": "dashboard", "action": "read"},
#         {"resource": "users", "action": "manage"},
#     ]

#     #  Insert permissions if not exist
#     permissions_map = {}

#     for perm in permissions_data:
#         result = await db.execute(
#             select(Permission).where(
#                 Permission.resource == perm["resource"],
#                 Permission.action == perm["action"],
#             )
#         )
#         obj = result.scalar_one_or_none()

#         if not obj:
#             obj = Permission(**perm)
#             db.add(obj)
#             await db.flush()

#         permissions_map[(perm["resource"], perm["action"])] = obj

#     #  Define roles
#     roles_data = {
#         "VIEWER": [
#             ("dashboard", "read"),
#         ],
#         "ANALYST": [
#             ("dashboard", "read"),
#             ("financial_records", "read"),
#         ],
#         "ADMIN": [
#             ("dashboard", "read"),
#             ("financial_records", "read"),
#             ("financial_records", "create"),
#             ("financial_records", "update"),
#             ("financial_records", "delete"),
#             ("users", "manage"),
#         ],
#     }

#     #  Insert roles + mappings
#     for role_name, perms in roles_data.items():
#         result = await db.execute(
#             select(Role).where(Role.name == role_name)
#         )
#         role = result.scalar_one_or_none()

#         if not role:
#             role = Role(name=role_name)
#             db.add(role)
#             await db.flush()

#         for resource, action in perms:
#             perm = permissions_map[(resource, action)]

#             result = await db.execute(
#                 select(role_permission).where(
#                     role_permission.role_id == role.id,
#                     role_permission.permission_id == perm.id,
#                 )
#             )

#             exists = result.scalar_one_or_none()

#             if not exists:
#                 db.add(
#                     role_permission(
#                         role_id=role.id,
#                         permission_id=perm.id,
#                     )
#                 )

#     await db.commit()