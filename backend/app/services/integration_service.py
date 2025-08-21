import base64
from typing import Optional
from datetime import datetime

from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from ..config import settings
from ..models.integration import Integration

class IntegrationService:
    """Service layer for handling provider integrations.

    Tokens for external providers are encrypted before being persisted and
    decrypted on access using a Fernet symmetric key derived from the
    application ``secret_key`` setting.
    """

    def __init__(self) -> None:
        key = settings.secret_key.encode()
        fernet_key = base64.urlsafe_b64encode(key.ljust(32)[:32])
        self._cipher = Fernet(fernet_key)

    # ------------------------------------------------------------------
    # Encryption helpers
    # ------------------------------------------------------------------
    def encrypt_token(self, token: Optional[str]) -> Optional[str]:
        """Return an encrypted representation of ``token``.

        ``None`` values are returned unmodified to simplify persistence logic.
        """

        if token is None:
            return None
        return self._cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: Optional[str]) -> Optional[str]:
        """Return the decrypted value of ``encrypted_token``.

        ``None`` values are returned unmodified to simplify retrieval logic.
        """

        if encrypted_token is None:
            return None
        return self._cipher.decrypt(encrypted_token.encode()).decode()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    async def store_tokens(
        self,
        db: Session,
        integration: Integration,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None,
    ) -> Integration:
        """Persist tokens for an ``Integration`` instance.

        Tokens are encrypted prior to being stored on the model instance.
        """

        integration.encrypted_access_token = self.encrypt_token(access_token)
        integration.encrypted_refresh_token = self.encrypt_token(refresh_token)
        integration.token_expiry = token_expiry

        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration
