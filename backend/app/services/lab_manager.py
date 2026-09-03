import docker
import requests
import secrets
from typing import Dict, Optional
import logging
from models import base
from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared Docker client so multiple LabManager instances don't each retry (and log) a failed connection
_docker_client = None
_docker_init_attempted = False


def _get_docker_client():
    global _docker_client, _docker_init_attempted
    if not _docker_init_attempted:
        _docker_init_attempted = True
        try:
            # Initialize Docker client (only if Docker is available)
            _docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(
                f"{type(e).__name__}: Docker unavailable, labs will use their external URLs"
            )
            _docker_client = None
    return _docker_client


class LabManager:
    def __init__(self):
        self.docker_client = _get_docker_client()

    def get_lab_by_id(self, lab_id: int, db = next(get_db())) -> Optional[Dict]:
        labs = db.query(
            base.Lab.external_url,
            base.Lab.docker_image,
            base.Lab.name,
            base.Lab.port
            ).filter(base.Lab.id == lab_id).first()
        if labs:
            return labs.__dict__
        return None

    def start_lab(self, lab_id: int) -> bool:
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return False

        try:
            # Build the image if it doesn't exist
            lab_dir = f"../../docker/labs/{lab['name'].lower().replace(' ', '-')}"
            image_name = lab["docker_image"]

            # Check if image exists
            try:
                self.docker_client.images.get(image_name)
            except docker.errors.ImageNotFound:
                # Build the image
                logger.info(f"Building image for {lab['name']}...")
                self.docker_client.images.build(path=lab_dir, tag=image_name, rm=True)
                logger.info(f"Built image for {lab['name']}")

            # Remove existing container if it exists
            try:
                container = self.docker_client.containers.get(
                    f"{lab['name'].lower().replace(' ', '-')}_lab"
                )
                container.stop()
                container.remove()
                logger.info(f"Removed existing container for {lab['name']}")
            except docker.errors.NotFound:
                pass

            # Start new container
            container = self.docker_client.containers.run(
                image=image_name,
                name=f"{lab['name'].lower().replace(' ', '-')}_lab",
                ports={f"{lab['port']}/tcp": lab["port"]},
                detach=True,
                network="attacksimulation_default",
                environment={"SECRET_KEY": secrets.token_hex(32)},
            )

            logger.info(f"Started container for {lab['name']} with ID: {container.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start lab {lab_id}: {str(e)}")
            return False

    def stop_lab(self, lab_id: int) -> bool:
        """
        Stop a vulnerable lab container
        """
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return False

        # Skip Docker operations if lab uses an external URL
        if lab.get("external_url"):
            logger.info(
                f"External lab at {lab['external_url']} does not require stopping."
            )
            return True

        # Skip Docker operations if Docker client is not available
        if not self.docker_client:
            logger.error("Docker client is not available. Cannot stop local lab.")
            return False

        try:
            container_name = f"{lab['name'].lower().replace(' ', '-')}_lab"
            container = self.docker_client.containers.get(container_name)
            container.stop()
            logger.info(f"Stopped container for {lab['name']}")
            return True
        except docker.errors.NotFound:
            logger.info(f"Container {container_name} not found")
            return True
        except Exception as e:
            logger.error(f"Failed to stop lab {lab_id}: {str(e)}")
            return False

    def reset_lab(self, lab_id: int) -> bool:
        """
        Reset a vulnerable lab to its initial state
        """
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return False

        # Skip reset for external labs (no action needed)
        if lab.get("external_url"):
            logger.info(
                f"External lab at {lab['external_url']} does not require reset."
            )
            return True

        # Stop the lab
        if not self.stop_lab(lab_id):
            return False

        # Start the lab
        return self.start_lab(lab_id)

    def delete_lab(self, lab_id: int) -> bool:
        """
        Delete a vulnerable lab (stop and remove)
        """
        # Stop the lab
        if not self.stop_lab(lab_id):
            return False

        # Note: We don't remove the Docker image as it's needed for future use
        # We just stop and remove the container
        return True

    def get_lab_status(self, lab_id: int) -> str:
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return "error"

        # Check if lab uses an external URL
        if lab.get("external_url"):
                response = requests.get(lab["external_url"], timeout=100)
        
                if response.status_code == 200:
                    return "running"
                return "error"

        # Skip Docker operations if Docker client is not available
        if not self.docker_client:
            logger.error("Docker client is not available. Cannot check local lab status.")
            return "error"

        try:
            container_name = f"{lab['name'].lower().replace(' ', '-')}_lab"
            container = self.docker_client.containers.get(container_name)

            # Check health status if available
            if (
                container.status == "running"
                and container.attrs["State"]["Health"]["Status"] == "healthy"
            ):
                return "running"
            elif container.status == "running":
                return "starting"
            else:
                return "stopped"

        except docker.errors.NotFound:
            return "stopped"
        except Exception as e:
            logger.error(f"Error checking lab {lab_id} status: {str(e)}")
            return "error"
