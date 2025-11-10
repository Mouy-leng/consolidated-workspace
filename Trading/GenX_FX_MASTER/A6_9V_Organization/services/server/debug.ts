
import { Request, Response, NextFunction } from 'express';

export function debugMiddleware(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  
  console.log(`🔍 [${new Date().toISOString()}] ${req.method} ${req.url}`);
  
  if (req.body && Object.keys(req.body).length > 0) {
    console.log('📝 Request body:', JSON.stringify(req.body, null, 2));
  }
  
  if (req.query && Object.keys(req.query).length > 0) {
    console.log('🔍 Query params:', req.query);
  }
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`✅ [${new Date().toISOString()}] ${req.method} ${req.url} - ${res.statusCode} (${duration}ms)`);
  });
  
  next();
}

export function errorLogger(err: Error, req: Request, res: Response, next: NextFunction) {
  console.error('❌ Error occurred:');
  console.error('📍 Route:', req.method, req.url);
  console.error('🚨 Error:', err.message);
  console.error('📚 Stack:', err.stack);
  
  if (req.body) {
    console.error('📝 Request body:', JSON.stringify(req.body, null, 2));
  }
  
  next(err);
}

export async function healthCheck(): Promise<{ status: string; details: any }> {
  const details = {
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    environment: process.env.NODE_ENV || 'development',
    nodeVersion: process.version,
    platform: process.platform
  };
  
  return {
    status: 'healthy',
    details
  };
}
