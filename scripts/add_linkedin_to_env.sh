#!/bin/bash

# Script to add LinkedIn credentials to .env file
# Usage: bash add_linkedin_to_env.sh

echo "Adding LinkedIn credentials to .env file..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file first by copying .env.example"
    exit 1
fi

# Check if LinkedIn credentials already exist
if grep -q "LINKEDIN_CLIENT_ID" .env; then
    echo "Warning: LinkedIn credentials already exist in .env"
    echo "Do you want to update them? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Aborted."
        exit 0
    fi
    # Remove existing LinkedIn credentials
    sed -i.bak '/LINKEDIN_/d' .env
fi

# Add LinkedIn credentials
cat >> .env << 'EOF'

# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=862bzxgrofi7oq
LINKEDIN_CLIENT_SECRET=WPL_AP1.yNfu7MmVzHqPBNOH.IFgRIA==
LINKEDIN_ACCESS_TOKEN=AQU6n3dlf1gzY8R-spVG2Kyc0diTzNqJ0jENMz49At2f07Jgf13VZVj1W04460taF-IQdb2Jkgy8Ui0qh29Nd-4wkfi_cVyOWZRkYP0ickPZda41qVawn85gCHvK1GSLiETUDZPat1ciXx3Lrk-Mm-1p7YQeYdEveEQ_ZqDU7a910F8xsh_sTQRHPxHrB7MasVk8gp234HDqLo66xhODuNoAy55zdQQxUElUWOP_TdOW5ThrBtO26omCBMbmlvzH29o2JN7ptrbcQTFLAClMNw-FJTCn86_B-5zNJGrpnb38TFOJa-Xe5_dLeDyQzA7aI64TL7bRs9C5_mA5albVX62EWIb4GA
EOF

echo "✅ LinkedIn credentials added to .env file!"
echo ""
echo "⚠️  IMPORTANT SECURITY REMINDER:"
echo "1. These credentials were shared publicly and should be revoked"
echo "2. Go to https://www.linkedin.com/developers/apps"
echo "3. Regenerate your Client Secret and Access Token"
echo "4. Update the .env file with new credentials"
echo ""
echo "Test credentials with:"
echo "python -c \"from dotenv import load_dotenv; import os; load_dotenv(); print('LinkedIn Client ID:', os.getenv('LINKEDIN_CLIENT_ID'))\""
