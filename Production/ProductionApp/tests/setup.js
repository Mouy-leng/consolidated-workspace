const mongoose = require('mongoose');

// Suppress deprecation warnings
mongoose.set('strictQuery', false);

// Setup test database
beforeAll(async () => {
  const MONGODB_URI = process.env.TEST_MONGODB_URI || 'mongodb://localhost:27017/productionapp-test';
  
  try {
    await mongoose.connect(MONGODB_URI, {
      useUnifiedTopology: true,
    });
  } catch (error) {
    console.error('Error connecting to test database:', error);
    process.exit(1);
  }
});

// Cleanup after tests
afterEach(async () => {
  if (mongoose.connection.db) {
    const collections = await mongoose.connection.db.collections();
    
    for (let collection of collections) {
      await collection.deleteMany({});
    }
  }
});

// Close database connection after all tests
afterAll(async () => {
  await mongoose.connection.close();
});