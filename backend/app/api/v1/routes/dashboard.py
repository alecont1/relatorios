"""
Dashboard metrics API endpoint.

Returns aggregated metrics for the current tenant:
- Reports by status, by month, by template, by user, by project
- Average completion time
- Total photos
- Certificate statistics
"""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, and_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_tenant_filter
from app.models.report import Report
from app.models.report_photo import ReportPhoto
from app.models.calibration_certificate import CalibrationCertificate
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# --- Response Schemas ---

class StatusCount(BaseModel):
    status: str
    count: int

class MonthCount(BaseModel):
    month: str  # "YYYY-MM"
    count: int

class TemplateCount(BaseModel):
    template_name: str
    count: int

class UserCount(BaseModel):
    user_id: str
    user_name: str
    count: int

class ProjectCount(BaseModel):
    project_id: str
    project_name: str
    count: int

class CertificateStats(BaseModel):
    total: int
    expiring_in_30_days: int
    expired: int

class DashboardMetrics(BaseModel):
    reports_by_status: list[StatusCount]
    reports_by_month: list[MonthCount]
    reports_by_template: list[TemplateCount]
    reports_by_user: list[UserCount]
    reports_by_project: list[ProjectCount]
    avg_completion_hours: float | None
    total_reports: int
    total_photos: int
    certificate_stats: CertificateStats


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: UUID | None = Depends(get_tenant_filter),
):
    """
    Get aggregated dashboard metrics for the current tenant.
    """
    # Base condition for tenant filtering
    conditions = []
    if tenant_id is not None:
        conditions.append(Report.tenant_id == tenant_id)

    # 1. Reports by status
    status_query = (
        select(Report.status, func.count(Report.id).label("count"))
        .where(and_(*conditions) if conditions else True)
        .group_by(Report.status)
    )
    status_result = await db.execute(status_query)
    reports_by_status = [
        StatusCount(status=row.status, count=row.count)
        for row in status_result.all()
    ]

    # Total reports
    total_reports = sum(s.count for s in reports_by_status)

    # 2. Reports by month (last 12 months)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    month_conditions = list(conditions) + [Report.created_at >= twelve_months_ago]
    month_query = (
        select(
            func.to_char(Report.created_at, 'YYYY-MM').label("month"),
            func.count(Report.id).label("count"),
        )
        .where(and_(*month_conditions))
        .group_by(func.to_char(Report.created_at, 'YYYY-MM'))
        .order_by(func.to_char(Report.created_at, 'YYYY-MM'))
    )
    month_result = await db.execute(month_query)
    reports_by_month = [
        MonthCount(month=row.month, count=row.count)
        for row in month_result.all()
    ]

    # 3. Reports by template (top 10)
    template_query = (
        select(
            Report.template_snapshot['name'].astext.label("template_name"),
            func.count(Report.id).label("count"),
        )
        .where(and_(*conditions) if conditions else True)
        .group_by(Report.template_snapshot['name'].astext)
        .order_by(func.count(Report.id).desc())
        .limit(10)
    )
    template_result = await db.execute(template_query)
    reports_by_template = [
        TemplateCount(template_name=row.template_name or "Sem nome", count=row.count)
        for row in template_result.all()
    ]

    # 4. Reports by user (top 10)
    from app.models.user import User as UserModel
    user_query = (
        select(
            Report.user_id,
            UserModel.full_name.label("user_name"),
            func.count(Report.id).label("count"),
        )
        .join(UserModel, Report.user_id == UserModel.id)
        .where(and_(*conditions) if conditions else True)
        .group_by(Report.user_id, UserModel.full_name)
        .order_by(func.count(Report.id).desc())
        .limit(10)
    )
    user_result = await db.execute(user_query)
    reports_by_user = [
        UserCount(user_id=str(row.user_id), user_name=row.user_name, count=row.count)
        for row in user_result.all()
    ]

    # 5. Reports by project (top 10)
    from app.models.project import Project
    project_query = (
        select(
            Report.project_id,
            Project.name.label("project_name"),
            func.count(Report.id).label("count"),
        )
        .join(Project, Report.project_id == Project.id)
        .where(and_(*conditions) if conditions else True)
        .group_by(Report.project_id, Project.name)
        .order_by(func.count(Report.id).desc())
        .limit(10)
    )
    project_result = await db.execute(project_query)
    reports_by_project = [
        ProjectCount(project_id=str(row.project_id), project_name=row.project_name, count=row.count)
        for row in project_result.all()
    ]

    # 6. Average completion time (draft -> completed)
    avg_query = (
        select(
            func.avg(
                extract('epoch', Report.completed_at) - extract('epoch', Report.started_at)
            ).label("avg_seconds")
        )
        .where(
            and_(
                *(conditions + [
                    Report.status == 'completed',
                    Report.started_at.isnot(None),
                    Report.completed_at.isnot(None),
                ])
            )
        )
    )
    avg_result = await db.execute(avg_query)
    avg_seconds = avg_result.scalar()
    avg_completion_hours = round(avg_seconds / 3600, 1) if avg_seconds else None

    # 7. Total photos
    photo_conditions = []
    if tenant_id is not None:
        # Photos are linked via report, so join
        photo_query = (
            select(func.count(ReportPhoto.id))
            .join(Report, ReportPhoto.report_id == Report.id)
            .where(Report.tenant_id == tenant_id)
        )
    else:
        photo_query = select(func.count(ReportPhoto.id))
    photo_result = await db.execute(photo_query)
    total_photos = photo_result.scalar() or 0

    # 8. Certificate stats
    cert_conditions = []
    if tenant_id is not None:
        cert_conditions.append(CalibrationCertificate.tenant_id == tenant_id)
    cert_conditions.append(CalibrationCertificate.is_active == True)

    today = datetime.utcnow().date()
    thirty_days = today + timedelta(days=30)

    cert_total_query = (
        select(func.count(CalibrationCertificate.id))
        .where(and_(*cert_conditions))
    )
    cert_total_result = await db.execute(cert_total_query)
    cert_total = cert_total_result.scalar() or 0

    cert_expiring_query = (
        select(func.count(CalibrationCertificate.id))
        .where(
            and_(
                *cert_conditions,
                CalibrationCertificate.expiry_date > today,
                CalibrationCertificate.expiry_date <= thirty_days,
            )
        )
    )
    cert_expiring_result = await db.execute(cert_expiring_query)
    cert_expiring = cert_expiring_result.scalar() or 0

    cert_expired_query = (
        select(func.count(CalibrationCertificate.id))
        .where(
            and_(
                *cert_conditions,
                CalibrationCertificate.expiry_date <= today,
            )
        )
    )
    cert_expired_result = await db.execute(cert_expired_query)
    cert_expired = cert_expired_result.scalar() or 0

    return DashboardMetrics(
        reports_by_status=reports_by_status,
        reports_by_month=reports_by_month,
        reports_by_template=reports_by_template,
        reports_by_user=reports_by_user,
        reports_by_project=reports_by_project,
        avg_completion_hours=avg_completion_hours,
        total_reports=total_reports,
        total_photos=total_photos,
        certificate_stats=CertificateStats(
            total=cert_total,
            expiring_in_30_days=cert_expiring,
            expired=cert_expired,
        ),
    )
