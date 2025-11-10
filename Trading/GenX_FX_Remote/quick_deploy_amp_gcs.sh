#!/bin/bash

# Quick AMP System GCS Deployment
# Simplified deployment script for rapid deployment

set -e

# Configuration
PROJECT_ID="fortress-notes-omrjz"
REGION="us-central1"
SERVICE_NAME="amp-trading-system"
BUCKET_NAME="amp-trading-system-data"
AMP_TOKEN="sgamp_user_01K1XBP8C5SZXYP88QD166AX1W_72c12a40546c130db17817dc9c92cb3770ecbe93e34a9fd23c8e9a2daa8e942c"
GITHUB_TOKEN="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"

echo "🚀 Quick AMP System GCS Deployment"
echo "=================================="

# Create service account key
cat > service-account-key.json << 'EOF'
{"type":"service_account","project_id":"fortress-notes-omrjz","private_key_id":"b67d0718617b5bbd69b98e61361475c2932c36ea","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDZMiVl1fAqt5Rj\ntmLOt+ZxWTRd9cE6gSKTjuXQ7Y74dkqW6g+8fff0+SDjM3D8Tlt5ic/VzXUoLC4n\nZ+ssqD6r7VTsc3lfWHWCX5dxsEXNcNfLJwXWVRoftw/43f/lf4G++87/4pSOulfF\nPVKnbWdwS0SZQ7ArmDl3LBTyyWcsVyVtuIXWOp341q2tWhBQg7fvhOoz5UamO8M2\n/pCVtWbGief0+V8dOf21X4FTB6HDzgxIe9iqjvOMGKaMwtSW2/59prno+H8MUWZN\nWPp2BNTf1a/lXpH0ek3CNGaSZsGVLb5CGSFtfGYnEUhyY/dsFIKzQvz1OUtnOy9m\nLn3AHhrLAgMBAAECggEAZ9jhJrLG1TXXXmGrFpm5NgLn1fEWBYoO5SyS13VuQYAV\no9if04kLUHb5cYh8AjbY5+CrnddRp/aPzsmSGVUMOhoM281Of/cEoGRiPbqBdXv5\nwamT0en4xqc5nM1QeAOiHpW5YIGOdDvGkYkDhwf5SCjE0N8bUYzEFSXfkkIX8YuL\nO3Ys49TzTP7n7RD/9LGdlIK8Z/GGThuAWbDdXTCNhlmOr8vQfiVRgwiOogbEof1V\nF7ro72ULufo/KhugO7GcohpRenEqqH527hSPuRT7a9k9L2lMxgWElmYQqBpN1mNv\nk9QfqAZKCtvx5fjEDgHCM8PjJnd3gMGSKlW4T3soMQKBgQD+JiTd6OT/eYbxgFQS\nH4/WZRCw2dw/PxdacrivCAACh4VMKfHodBQlRxRXJmN/uialw34r+UW2B5vz54qq\nCf3ciWYqNQbZjnCLuEzDUVEtf2sb/z81LJEocvpUHc62NUDdJh4uZkp9Ww19khuK\nweuST+7nWLAny2ftp20Ol3HjkwKBgQDaxxqLV0ojttLLl6wb3cmuj3WhQe9bgW8k\ng8mDGBjcaHZt+3ScAU84UQ/D19f/W+Y7yoHt/85VSpilPnpc9p5bTuu4u8YCxupH\nPnXcRALB9mRHT2LZ+NIgYj+5odrVNirW1nU48aCPb0eetgHOAFP99j6uJ5i8Rog5\n6T1IZEJe6QKBgQCU1+YTiMhEzvm3Cn8yNgXZfEswKAeTivG0aSe8aqUG1jO9DXu9\nte3ufxhsifEP5wenYTzNqCmpl/8/80UEnOFufZG1+mROmdtUGNXsNf2i9dLXDMAJ\n9lX1KJFvHh3oHHwmiKJ4bjQGAoN+HUnAFB5RDDtQhmJ0i+4MA1gdiZiLvQKBgQDP\nTQge7mhG7Q5ScfZYNVDMgg0Q7twyFbRNoj6IZIXyG13UmwcEZ8077LuGc/isc9T1\n5M42yUQm11dKhKgHfHvSwzZixjI7IWaOeWXOf/co+SJN27AsIDRjERWW/QHRM9Fl\n3rIWcgYUw3nWrlmJbBAqPXFpLgXwqNieHx69gJrPOQKBgQDAAirRqBvO/uMgtgHk\nNxHgG7y96jmEPP1vsZ0Z/nfQmOe2kkQkuVx4TXtm4LIVWRq+6kzWkVqJGEKR61tz\n2YN4wtrt80z9JZnrsHyCnox5ABJkuol59XYGmDzjsEML2l2EkfXjCb/rwkPupZmy\nJz02VQpwX4VqyEvRqKhwVl43gg==\n-----END PRIVATE KEY-----\n","client_email":"723463751699-compute@developer.gserviceaccount.com","client_id":"116640863077293757833","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/723463751699-compute%40developer.gserviceaccount.com","universe_domain":"googleapis.com"}
EOF

echo "✅ Service account key created"

# Install gcloud if not available
if ! command -v gcloud &> /dev/null; then
    echo "📥 Installing Google Cloud CLI..."
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    source ~/.bashrc
fi

echo "✅ Google Cloud CLI ready"

# Authenticate and set project
gcloud config set project $PROJECT_ID
gcloud auth activate-service-account --key-file=service-account-key.json

echo "✅ Authenticated with Google Cloud"

# Create GCS bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "ℹ️  Bucket already exists"

echo "✅ GCS bucket ready"

# Create deployment package
tar -czf amp-system.tar.gz \
    amp_cli.py \
    amp_config.json \
    amp_auth.json \
    amp-plugins/ \
    requirements-amp.txt \
    docker-compose.amp.yml \
    --exclude='*.pyc' \
    --exclude='__pycache__'

echo "✅ Deployment package created"

# Upload to GCS
gsutil cp amp-system.tar.gz gs://$BUCKET_NAME/
gsutil cp amp_config.json gs://$BUCKET_NAME/
gsutil cp amp_auth.json gs://$BUCKET_NAME/

echo "✅ Files uploaded to GCS"

# Create Dockerfile for Cloud Run
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-amp.txt .
RUN pip install -r requirements-amp.txt

# Copy application files
COPY amp_cli.py .
COPY amp_config.json .
COPY amp_auth.json .
COPY amp-plugins/ ./amp-plugins/

# Create startup script
RUN echo '#!/bin/bash\npython3 amp_cli.py status' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 8080

# Start the application
CMD ["python3", "amp_cli.py", "status"]
EOF

echo "✅ Dockerfile created"

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "AMP_TOKEN=$AMP_TOKEN,GITHUB_TOKEN=$GITHUB_TOKEN,PROJECT_ID=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME"

echo "✅ Deployed to Cloud Run"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "Service URL will be available after deployment completes")

echo ""
echo "🎉 AMP System GCS Deployment Complete!"
echo "======================================"
echo "GCS Bucket: gs://$BUCKET_NAME"
echo "Cloud Run Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "Service URL: $SERVICE_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Monitor: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "2. Logs: gcloud logs tail --service=$SERVICE_NAME"
echo "3. Access: gcloud run services call $SERVICE_NAME --region=$REGION"