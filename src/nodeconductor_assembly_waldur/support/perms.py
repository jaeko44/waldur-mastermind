from nodeconductor.core.permissions import StaffPermissionLogic

PERMISSION_LOGICS = (
    ('support.Issue', StaffPermissionLogic(any_permission=True)),
)