# app/api/api_v1/api.py
from fastapi import APIRouter, HTTPException
import httpx
from my_service.models.models import ApplicationStatusResponse, ProjectsResponse, ApplicationStatus, Project
from my_service.config.config import settings
from my_service.utils.logger import setup_logger

router = APIRouter(prefix="/api/v1")
logger = setup_logger()

@router.get("/argocd/application_status", response_model=ApplicationStatusResponse)
async def get_application_status():
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                f"http://{settings.ARGOCD_URL}/api/v1/applications",
                headers={"Authorization": f"Bearer {settings.ARGOCD_AUTH_TOKEN}"}
            )
            if response.status_code == 200:
                applications = response.json().get('items', [])
                app_statuses = [
                    ApplicationStatus(
                        application_name=app['metadata']['name'],
                        status=app.get('status', {}).get('sync', {}).get('status', 'Unknown')
                    )
                    for app in applications
                ]
                return ApplicationStatusResponse(applications=app_statuses)
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get applications")
    except Exception as e:
        logger.error(f"Error getting application status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/argocd/list_projects", response_model=ProjectsResponse)
async def list_projects():
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(
                f"http://{settings.ARGOCD_URL}/api/v1/projects",
                headers={"Authorization": f"Bearer {settings.ARGOCD_AUTH_TOKEN}"}
            )
            if response.status_code == 200:
                projects = response.json().get('items', [])
                project_list = [
                    Project(
                        project_name=project['metadata']['name'],
                        namespace=project['metadata'].get('namespace', 'argocd')
                    )
                    for project in projects
                ]
                return ProjectsResponse(projects=project_list)
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get projects")
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
