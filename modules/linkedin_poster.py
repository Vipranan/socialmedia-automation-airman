"""
Module: linkedin_poster.py
Publishes image posts to LinkedIn using the v2 API (no versioning header needed).

Flow:
  1. GET  /v2/me                         — fetch person URN
  2. POST /v2/assets?action=registerUpload — register image
  3. PUT  {uploadUrl}                     — upload image binary
  4. POST /v2/ugcPosts                    — publish post
"""

import logging
import requests
from config.settings import LINKEDIN_ACCESS_TOKEN

logger = logging.getLogger(__name__)

_BASE = "https://api.linkedin.com/v2"


def _headers(content_type: str = "application/json") -> dict:
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": content_type,
    }


def _raise_with_body(resp: requests.Response) -> None:
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(f"{e} | Response: {resp.text}", response=resp) from e


def _get_person_urn() -> str:
    resp = requests.get(f"{_BASE}/me", headers=_headers(), timeout=15)
    _raise_with_body(resp)
    person_id = resp.json().get("id")
    if not person_id:
        raise ValueError(f"Could not fetch LinkedIn person ID. Response: {resp.text}")
    urn = f"urn:li:person:{person_id}"
    logger.info(f"LinkedIn person URN: {urn}")
    return urn


def _register_image_upload(person_urn: str) -> tuple[str, str]:
    """Returns (asset_urn, upload_url)."""
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    resp = requests.post(
        f"{_BASE}/assets?action=registerUpload",
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    _raise_with_body(resp)
    data = resp.json()
    asset_urn  = data["value"]["asset"]
    upload_url = data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    logger.info(f"LinkedIn asset URN: {asset_urn}")
    return asset_urn, upload_url


def _upload_image(upload_url: str, image_path: str) -> None:
    with open(image_path, "rb") as f:
        resp = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "application/octet-stream",
            },
            data=f,
            timeout=60,
        )
    _raise_with_body(resp)
    logger.info("Image uploaded to LinkedIn.")


def _create_post(person_urn: str, asset_urn: str, caption: str) -> str:
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption[:3000]},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "Aviation news"},
                        "media": asset_urn,
                    }
                ],
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }
    resp = requests.post(
        f"{_BASE}/ugcPosts",
        headers=_headers(),
        json=payload,
        timeout=15,
    )
    _raise_with_body(resp)
    post_id = resp.headers.get("x-restli-id", "unknown")
    logger.info(f"LinkedIn post published. Post ID: {post_id}")
    return post_id


def post_to_linkedin(image_path: str, caption: str) -> str:
    person_urn = _get_person_urn()
    asset_urn, upload_url = _register_image_upload(person_urn)
    _upload_image(upload_url, image_path)
    return _create_post(person_urn, asset_urn, caption)
