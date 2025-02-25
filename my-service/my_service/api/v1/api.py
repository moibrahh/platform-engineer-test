# app/api/api_v1/api.py
from fastapi import APIRouter, HTTPException
import httpx
from my_service.models.models import ApplicationStatusResponse, ProjectsResponse, ApplicationStatus, Project
from my_service.config.config import settings
from my_service.utils.logger import setup_logger
from cachetools import TTLCache
import subprocess
import base64

router = APIRouter(prefix="/api/v1")
logger = setup_logger()

# Cache for storing ArgoCD token
token_cache = TTLCache(maxsize=1, ttl=settings.TOKEN_CACHE_TTL)

async def get_argocd_password():
    """Get ArgoCD password from k8s secret"""
    try:
        # Get password from k8s secret
        cmd = "kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}'"
        encoded_password = subprocess.check_output(cmd, shell=True).decode('utf-8')
        password = base64.b64decode(encoded_password).decode('utf-8')
        return password.strip()
    except Exception as e:
        logger.error(f"Error getting ArgoCD password: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get ArgoCD credentials")

async def get_argocd_token():
    """Get ArgoCD authentication token"""
    if 'token' in token_cache:
        return token_cache['token']
    
    try:
        # Get fresh password
        password = await get_argocd_password()
        
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            response = await client.post(
                f"https://{settings.ARGOCD_URL}/api/v1/session",
                json={
                    "username": "admin",
                    "password": password
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    token_cache['token'] = token
                    return token
            
            logger.error(f"Auth failed: Status {response.status_code}, Response: {response.text}")
            raise HTTPException(status_code=401, detail=f"Authentication failed: {response.text}")
            
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# First required endpoint: GET /api/v1/argocd/application_status
@router.get("/argocd/application_status", response_model=ApplicationStatusResponse)
async def get_application_status():
    """
    Get status of all ArgoCD applications
    Returns: {
        "applications": [
            {
                "application_name": "my-service",
                "status": "Synced"
            },
            {
                "application_name": "nginx",
                "status": "Synced"
            }
        ]
    }
    """
    try:
        token = await get_argocd_token()
        
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            response = await client.get(
                f"https://{settings.ARGOCD_URL}/api/v1/applications",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
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
                logger.error(f"Failed to get applications: Status {response.status_code}, Response: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to get applications: {response.text}")
    except Exception as e:
        logger.error(f"Error getting application status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Second required endpoint: GET /api/v1/argocd/list_projects
@router.get("/argocd/list_projects", response_model=ProjectsResponse)
async def list_projects():
    """
    List all ArgoCD projects
    Returns: {
        "projects": [
            {
                "project_name": "default",
                "namespace": "argocd"
            }
        ]
    }
    """
    try:
        token = await get_argocd_token()
        
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            response = await client.get(
                f"https://{settings.ARGOCD_URL}/api/v1/projects",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
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
                logger.error(f"Failed to get projects: Status {response.status_code}, Response: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Failed to get projects: {response.text}")
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
