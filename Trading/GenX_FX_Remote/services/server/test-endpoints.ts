
import { db } from './db.js';
import { users, tradingAccounts, positions, notifications, educationalResources } from '../shared/schema.js';

export async function testDatabaseConnections() {
  console.log('🧪 Testing database connections...');
  
  try {
    // Test basic connection
    const result = await db.select().from(users).limit(1);
    console.log('✅ Database connection successful');
    
    // Test each table
    const tables = [
      { name: 'users', table: users },
      { name: 'tradingAccounts', table: tradingAccounts },
      { name: 'positions', table: positions },
      { name: 'notifications', table: notifications },
      { name: 'educationalResources', table: educationalResources }
    ];
    
    for (const { name, table } of tables) {
      try {
        await db.select().from(table).limit(1);
        console.log(`✅ Table ${name} accessible`);
      } catch (error) {
        console.log(`❌ Table ${name} error:`, error.message);
      }
    }
    
    return true;
  } catch (error) {
    console.error('❌ Database connection failed:', error);
    return false;
  }
}

export async function seedTestData() {
  console.log('🌱 Seeding test data...');
  
  try {
    // Add test educational resource
    await db.insert(educationalResources).values({
      title: 'Getting Started with Trading',
      description: 'A comprehensive guide for beginners',
      type: 'article',
      skillLevel: 'beginner',
      category: 'basics',
      url: 'https://example.com/getting-started',
      estimatedReadTime: 15
    }).onConflictDoNothing();
    
    console.log('✅ Test data seeded successfully');
    return true;
  } catch (error) {
    console.error('❌ Failed to seed test data:', error);
    return false;
  }
}
