@echo off
echo 🔥 Firebase Manual Deployment
echo ============================

cd /d "C:\Users\USER\GenX_FX"

echo 🔐 Please login to Firebase manually...
echo Opening browser for authentication...

:: Manual login
firebase login

echo 🚀 Deploying to Firebase...
firebase use sample-firebase-ai-app-96331
firebase deploy --only hosting

echo ✅ Deployment completed!
echo 🌐 Your app should be live at: https://sample-firebase-ai-app-96331.firebaseapp.com
pause