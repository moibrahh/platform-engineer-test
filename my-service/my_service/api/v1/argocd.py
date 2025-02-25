from fastapi import APIRouter, HTTPException
from my_service.models.models import ApplicationStatusResponse, ProjectsResponse, ApplicationStatus, Project
from my_service.utils.logger import setup_logger
from my_service.config.config import settings
import httpx
from cachetools import TTLCache

router = APIRouter(prefix="/argocd", tags=["argocd"])
logger = setup_logger()

# Cache for storing ArgoCD token
token_cache = TTLCache(maxsize=1, ttl=settings.TOKEN_CACHE_TTL)

async def get_argocd_token():
    """Get ArgoCD authentication token"""
    if 'token' in token_cache:
        return token_cache['token']
    
    try:
        auth_url = f"http://{settings.ARGOCD_URL}/api/v1/session"  # Using HTTP
        auth_data = {
            "username": settings.ARGOCD_USERNAME,
            "password": settings.ARGOCD_PASSWORD.strip()
        }
        
        logger.debug(f"Attempting to authenticate with ArgoCD at {auth_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:  # Removed verify=False
            response = await client.post(
                auth_url,
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            logger.debug(f"Auth response status: {response.status_code}")
            logger.debug(f"Auth response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                if token:
                    token_cache['token'] = token
                    return token
            
            error_msg = f"Authentication failed: {response.text}"
            logger.error(error_msg)
            raise HTTPException(status_code=401, detail=error_msg)
            
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/application_status", response_model=ApplicationStatusResponse)
async def get_application_status():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/api/v1/applications")
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list_projects", response_model=ProjectsResponse)
async def list_projects():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/api/v1/projects")
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
        raise HTTPException(status_code=500, detail=str(e)) 