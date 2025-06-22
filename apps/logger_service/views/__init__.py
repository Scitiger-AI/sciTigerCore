"""
日志服务视图导入
"""

from .platform import (
    LogCategoryViewSet as PlatformLogCategoryViewSet,
    LogEntryViewSet as PlatformLogEntryViewSet,
    LogRetentionPolicyViewSet as PlatformLogRetentionPolicyViewSet
)

from .management import (
    LogCategoryViewSet as ManagementLogCategoryViewSet,
    LogEntryViewSet as ManagementLogEntryViewSet,
    LogRetentionPolicyViewSet as ManagementLogRetentionPolicyViewSet
)

__all__ = [
    'PlatformLogCategoryViewSet',
    'PlatformLogEntryViewSet',
    'PlatformLogRetentionPolicyViewSet',
    'ManagementLogCategoryViewSet',
    'ManagementLogEntryViewSet',
    'ManagementLogRetentionPolicyViewSet',
]
