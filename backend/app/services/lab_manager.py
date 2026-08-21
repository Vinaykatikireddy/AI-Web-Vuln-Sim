import docker
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LabManager:
    def __init__(self):
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            raise

    def get_available_labs(self) -> List[Dict]:
        """
        Get list of available labs from the labs directory
        """
        labs = [
            {
                "id": 1,
                "name": "Simple Login",
                "description": "Vulnerable login application with SQL Injection and weak authentication",
                "docker_image": "attack-simulation-login",
                "port": 5001,
                "vulnerabilities": ["SQL Injection", "Weak Authentication"]
            },
            {
                "id": 2,
                "name": "Blog",
                "description": "Blog application with Stored and Reflected XSS vulnerabilities",
                "docker_image": "attack-simulation-blog",
                "port": 5002,
                "vulnerabilities": ["Stored XSS", "Reflected XSS"]
            },
            {
                "id": 3,
                "name": "Ecommerce",
                "description": "Ecommerce application with IDOR vulnerabilities",
                "docker_image": "attack-simulation-ecommerce",
                "port": 5003,
                "vulnerabilities": ["IDOR", "Insecure Admin Panel"]
            },
            {
                "id": 4,
                "name": "File Upload",
                "description": "File upload service with unsafe file upload vulnerability",
                "docker_image": "attack-simulation-fileupload",
                "port": 5004,
                "vulnerabilities": ["Unsafe File Upload", "Path Traversal"]
            }
        ]
        return labs

    def get_lab_by_id(self, lab_id: int) -> Optional[Dict]:
        """
        Get a specific lab by ID
        """
        labs = self.get_available_labs()
        for lab in labs:
            if lab["id"] == lab_id:
                return lab
        return None

    def start_lab(self, lab_id: int) -> bool:
        """
        Start a vulnerable lab container
        """
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return False

        try:
            # Build the image if it doesn't exist
            lab_dir = f"../../docker/labs/{lab['name'].lower().replace(' ', '-')}"
            image_name = lab['docker_image']

            # Check if image exists
            try:
                self.docker_client.images.get(image_name)
            except docker.errors.ImageNotFound:
                # Build the image
                logger.info(f"Building image for {lab['name']}...")
                self.docker_client.images.build(
                    path=lab_dir,
                    tag=image_name,
                    rm=True
                )
                logger.info(f"Built image for {lab['name']}")

            # Remove existing container if it exists
            try:
                container = self.docker_client.containers.get(f"{lab['name'].lower().replace(' ', '-')}_lab")
                container.stop()
                container.remove()
                logger.info(f"Removed existing container for {lab['name']}")
            except docker.errors.NotFound:
                pass

            # Start new container
            container = self.docker_client.containers.run(
                image=image_name,
                name=f"{lab['name'].lower().replace(' ', '-')}_lab",
                ports={{f"{lab['port']}/tcp": lab['port']}},
                detach=True,
                network="attacksimulation_default",
                environment={{"SECRET_KEY": "lab-secret-key-123"}}
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
        """
        Get the status of a lab (running, stopped, error)
        """
        lab = self.get_lab_by_id(lab_id)
        if not lab:
            return "error"

        try:
            container_name = f"{lab['name'].lower().replace(' ', '-')}_lab"
            container = self.docker_client.containers.get(container_name)

            # Check health status if available
            if container.status == "running" and container.attrs['State']['Health']['Status'] == "healthy":
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