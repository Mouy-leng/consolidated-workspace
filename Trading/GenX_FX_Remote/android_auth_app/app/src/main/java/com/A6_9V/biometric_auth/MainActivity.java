package com.A6_9V.biometric_auth;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.biometric.BiometricPrompt.PromptInfo;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import java.io.FileOutputStream;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.concurrent.Executor;

public class MainActivity extends FragmentActivity {
    
    private static final String TAG = "BiometricAuth";
    private static final String AUTH_RESULT_FILE = "/data/local/tmp/biometric_result.txt";
    
    private BiometricPrompt biometricPrompt;
    private BiometricPrompt.PromptInfo promptInfo;
    private Executor executor;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        Log.d(TAG, "MainActivity started");
        
        // Check if launched via ADB intent
        Intent intent = getIntent();
        if (intent != null && "com.A6_9V.biometric_auth.AUTHENTICATE".equals(intent.getAction())) {
            Log.d(TAG, "Authentication request received via intent");
            handleAuthenticationRequest();
        } else {
            // Normal app launch - show UI or finish
            showBiometricAuthUI();
        }
    }
    
    private void handleAuthenticationRequest() {
        // Check biometric availability
        BiometricManager biometricManager = BiometricManager.from(this);
        
        switch (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK)) {
            case BiometricManager.BIOMETRIC_SUCCESS:
                Log.d(TAG, "Biometric authentication available");
                performBiometricAuthentication();
                break;
            case BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE:
                Log.e(TAG, "No biometric hardware available");
                writeAuthResult("ERROR", "No biometric hardware available");
                finish();
                break;
            case BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE:
                Log.e(TAG, "Biometric hardware unavailable");
                writeAuthResult("ERROR", "Biometric hardware unavailable");
                finish();
                break;
            case BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED:
                Log.e(TAG, "No biometric enrolled");
                writeAuthResult("ERROR", "No biometric enrolled");
                finish();
                break;
            default:
                Log.e(TAG, "Unknown biometric error");
                writeAuthResult("ERROR", "Unknown biometric error");
                finish();
                break;
        }
    }
    
    private void showBiometricAuthUI() {
        // Show simple UI for manual testing
        handleAuthenticationRequest();
    }
    
    private void performBiometricAuthentication() {
        executor = ContextCompat.getMainExecutor(this);
        
        biometricPrompt = new BiometricPrompt(this, executor, new BiometricPrompt.AuthenticationCallback() {
            @Override
            public void onAuthenticationError(int errorCode, @NonNull CharSequence errString) {
                super.onAuthenticationError(errorCode, errString);
                Log.e(TAG, "Authentication error: " + errString);
                writeAuthResult("FAILED", "Authentication error: " + errString);
                Toast.makeText(MainActivity.this, "Authentication error: " + errString, Toast.LENGTH_SHORT).show();
                finish();
            }
            
            @Override
            public void onAuthenticationSucceeded(@NonNull BiometricPrompt.AuthenticationResult result) {
                super.onAuthenticationSucceeded(result);
                Log.d(TAG, "Authentication succeeded");
                
                // Generate authentication token
                String authToken = generateAuthToken();
                writeAuthResult("SUCCESS", "Authentication successful", authToken);
                
                Toast.makeText(MainActivity.this, "Authentication successful!", Toast.LENGTH_SHORT).show();
                finish();
            }
            
            @Override
            public void onAuthenticationFailed() {
                super.onAuthenticationFailed();
                Log.w(TAG, "Authentication failed");
                Toast.makeText(MainActivity.this, "Authentication failed", Toast.LENGTH_SHORT).show();
                // Don't finish here - let user try again
            }
        });
        
        promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle("Biometric Authentication")
                .setSubtitle("Authenticate using your biometric credential")
                .setDescription("Use your fingerprint, face, or other biometric to authenticate")
                .setNegativeButtonText("Cancel")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_WEAK | 
                                        BiometricManager.Authenticators.DEVICE_CREDENTIAL)
                .build();
        
        biometricPrompt.authenticate(promptInfo);
    }
    
    private String generateAuthToken() {
        try {
            SecureRandom random = new SecureRandom();
            byte[] bytes = new byte[32];
            random.nextBytes(bytes);
            
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(bytes);
            
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            
            return hexString.toString();
        } catch (Exception e) {
            Log.e(TAG, "Error generating auth token", e);
            return "error_token";
        }
    }
    
    private void writeAuthResult(String status, String message) {
        writeAuthResult(status, message, null);
    }
    
    private void writeAuthResult(String status, String message, String token) {
        try {
            String result = "AUTH_STATUS=" + status + "\n" +
                           "AUTH_MESSAGE=" + message + "\n" +
                           "AUTH_TIMESTAMP=" + System.currentTimeMillis() + "\n";
            
            if (token != null) {
                result += "AUTH_TOKEN=" + token + "\n";
            }
            
            result += "DEVICE_MODEL=" + android.os.Build.MODEL + "\n" +
                     "DEVICE_MANUFACTURER=" + android.os.Build.MANUFACTURER + "\n" +
                     "ANDROID_VERSION=" + android.os.Build.VERSION.RELEASE + "\n";
            
            // Write to temp file that ADB can read
            FileOutputStream fos = new FileOutputStream(AUTH_RESULT_FILE);
            fos.write(result.getBytes());
            fos.close();
            
            Log.d(TAG, "Auth result written to " + AUTH_RESULT_FILE);
            Log.d(TAG, "Result: " + result);
            
        } catch (IOException e) {
            Log.e(TAG, "Error writing auth result", e);
        }
    }
}