"""LinkedIn service for posting content."""
import httpx
from src.logger import logger
from src.config import LINKEDIN_ACCESS_TOKEN


async def post_to_linkedin(text: str, image_path: str = None) -> dict:
    """Post content to LinkedIn."""
    try:
        logger.info("Posting to LinkedIn...")
        
        headers = {
            'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # Get user profile URN
        profile_url = 'https://api.linkedin.com/v2/me'
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(profile_url, headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            person_urn = f"urn:li:person:{profile_data['id']}"
            
            # Upload image if provided
            asset_urn = None
            if image_path:
                # Register upload
                register_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
                register_payload = {
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner": person_urn,
                        "serviceRelationships": [{
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }]
                    }
                }
                
                register_response = await client.post(register_url, json=register_payload, headers=headers)
                register_response.raise_for_status()
                register_data = register_response.json()
                
                upload_url = register_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
                asset_urn = register_data['value']['asset']
                
                # Upload image
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                upload_headers = {'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}'}
                upload_response = await client.put(upload_url, content=image_data, headers=upload_headers)
                upload_response.raise_for_status()
            
            # Create post
            share_url = 'https://api.linkedin.com/v2/ugcPosts'
            share_payload = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "IMAGE" if image_path else "NONE"
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            
            if asset_urn:
                share_payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "media": asset_urn
                }]
            
            share_response = await client.post(share_url, json=share_payload, headers=headers)
            share_response.raise_for_status()
            result = share_response.json()
            
            logger.info(f"Successfully posted to LinkedIn: {result.get('id', 'N/A')}")
            return result
            
    except Exception as e:
        logger.error(f"Failed to post to LinkedIn: {e}")
        raise


def validate_linkedin_credentials():
    """Validate LinkedIn credentials are present."""
    if LINKEDIN_ACCESS_TOKEN:
        logger.info("✅ LinkedIn credentials loaded successfully")
        return True
    else:
        logger.warning("⚠️ LinkedIn credentials not found")
        return False
