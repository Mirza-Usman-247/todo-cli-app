"""
Dapr Secrets Client Wrapper
Retrieves secrets from Kubernetes Secrets via Dapr
"""
from dapr.clients import DaprClient
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

STORE_NAME = "kubernetes-secrets"


class DaprSecretsClient:
    """Wrapper for Dapr Secrets API operations"""

    def __init__(self):
        self.store_name = STORE_NAME

    def get_secret(
        self,
        secret_name: str,
        key: Optional[str] = None
    ) -> Optional[str]:
        """
        Retrieve a secret from Kubernetes Secrets via Dapr

        Args:
            secret_name: Name of the secret in Kubernetes
            key: Specific key within the secret (if secret is a map)

        Returns:
            Secret value as string, or None if not found
        """
        try:
            with DaprClient() as client:
                # Get the secret from Kubernetes
                secret = client.get_secret(
                    store_name=self.store_name,
                    key=secret_name,
                )

                # If key is specified, get that specific value
                # Otherwise return the first value
                if key:
                    value = secret.secret.get(key)
                else:
                    # Get first value if secret is a key-value map
                    value = list(secret.secret.values())[0] if secret.secret else None

                if value:
                    logger.info(f"✅ Retrieved secret '{secret_name}' from Dapr")
                    return value
                else:
                    logger.warning(f"⚠️  Secret '{secret_name}' not found")
                    return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret '{secret_name}' via Dapr: {e}")
            return None

    def get_secret_bulk(self, secret_name: str) -> Dict[str, str]:
        """
        Retrieve all key-value pairs from a secret

        Args:
            secret_name: Name of the secret in Kubernetes

        Returns:
            Dictionary of all key-value pairs in the secret
        """
        try:
            with DaprClient() as client:
                secret = client.get_secret(
                    store_name=self.store_name,
                    key=secret_name,
                )

                if secret.secret:
                    logger.info(f"✅ Retrieved secret '{secret_name}' (bulk) from Dapr")
                    return secret.secret
                else:
                    logger.warning(f"⚠️  Secret '{secret_name}' not found")
                    return {}

        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret '{secret_name}' via Dapr: {e}")
            return {}


# Singleton instance
secrets_client = DaprSecretsClient()


# Convenience exports
__all__ = ['DaprSecretsClient', 'secrets_client']
