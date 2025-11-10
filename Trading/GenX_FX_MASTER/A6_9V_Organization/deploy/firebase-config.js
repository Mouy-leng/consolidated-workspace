// Firebase Configuration for GenX FX Frontend
// Auto-generated configuration

const firebaseConfig = {
  // Firebase project configuration
  apiKey: "your-api-key-here", // Replace with your Firebase API key
  authDomain: "your-project.firebaseapp.com", // Replace with your domain
  projectId: "your-project-id", // Replace with your project ID
  storageBucket: "your-project.appspot.com", // Replace with your storage bucket
  messagingSenderId: "123456789", // Replace with your sender ID
  appId: "your-app-id", // Replace with your app ID
  measurementId: "G-XXXXXXXXXX" // Replace with your measurement ID
};

// Authentication configuration with provided hash parameters
const authConfig = {
  hashConfig: {
    algorithm: "SCRYPT",
    base64SignerKey: "e2Iii842GAYWTag4u6n61P18DdL+sSLtgSm2fmPxAyGgYpiH5Y4C13m+LF++TF4zZ7a8TTEl3i8WT2PpAu/IKA==",
    base64SaltSeparator: "Bw==",
    rounds: 8,
    memCost: 14
  },
  // Test user configuration
  testUser: {
    email: "lengkundee01@gmail.com",
    token: "jmboQydL5KRqerZ6RAFRCABtkLp2"
  }
};

export { firebaseConfig, authConfig };