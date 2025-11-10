# ProductionApp

🚀 **Production-Ready Node.js Application** with Express, MongoDB, JWT Authentication, and comprehensive security features.

## ✨ Features

- **🔐 Secure Authentication** - JWT-based with account lockout protection
- **📊 Health Monitoring** - Comprehensive health checks and metrics
- **🛡️ Security First** - Helmet, CORS, rate limiting, input validation
- **🗄️ Database Integration** - MongoDB with Mongoose ODM
- **🧪 Testing Suite** - Jest with comprehensive test coverage
- **🐳 Docker Support** - Multi-stage builds with security scanning
- **⚡ CI/CD Pipeline** - GitHub Actions with automated testing and deployment
- **📝 API Documentation** - RESTful API with proper error handling
- **🔍 Logging & Monitoring** - Morgan logging with error tracking

## 🚦 Quick Start

### Prerequisites

- Node.js 18+ 
- MongoDB 6.0+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mouy-leng/ProductionApp.git
   cd ProductionApp
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start MongoDB**
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:6.0
   
   # Or use your local MongoDB installation
   ```

5. **Run the application**
   ```bash
   # Development
   npm run dev
   
   # Production
   npm start
   ```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t productionapp .

# Run container
docker run -p 3000:3000 --env-file .env productionapp
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | User login | ❌ |
| GET | `/api/auth/me` | Get current user | ✅ |
| POST | `/api/auth/logout` | User logout | ✅ |
| PUT | `/api/auth/profile` | Update profile | ✅ |

### User Management (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/:id` | Get user by ID |
| PUT | `/api/users/:id` | Update user |
| DELETE | `/api/users/:id` | Delete user |
| PUT | `/api/users/:id/unlock` | Unlock user account |
| GET | `/api/users/stats/overview` | User statistics |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/detailed` | Detailed system info |

### Example API Usage

**Register a new user:**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## 🔐 Security Features

- **JWT Authentication** with secure token generation
- **Account Lockout** after failed login attempts
- **Rate Limiting** to prevent abuse
- **Helmet.js** for security headers
- **CORS** configuration
- **Input Validation** and sanitization
- **Password Hashing** with bcrypt
- **Security Auditing** in CI/CD pipeline

## 📊 Monitoring & Health Checks

- **Health Endpoints** for load balancer integration
- **System Metrics** (memory, CPU, database status)
- **Docker Health Checks** for container orchestration
- **Application Logging** with Morgan
- **Error Tracking** with comprehensive error handling

## 🚀 Production Deployment

### Environment Variables

Required environment variables for production:

```bash
NODE_ENV=production
PORT=3000
MONGODB_URI=mongodb://localhost:27017/productionapp
JWT_SECRET=your-super-secure-jwt-secret
JWT_EXPIRE=7d
BCRYPT_SALT_ROUNDS=12
```

### Deployment Checklist

- [ ] Set strong JWT secret
- [ ] Configure MongoDB connection
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Set up CI/CD pipeline
- [ ] Security audit and penetration testing

## 🏗️ Project Structure

```
ProductionApp/
├── src/
│   ├── controllers/     # Route controllers
│   ├── middleware/      # Custom middleware
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── utils/          # Utility functions
│   └── server.js       # Main server file
├── config/             # Configuration files
├── tests/              # Test files
├── docs/               # Documentation
├── public/             # Static files
├── .github/workflows/  # CI/CD workflows
├── docker-compose.yml  # Docker compose config
├── Dockerfile          # Docker configuration
└── package.json        # Project dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the ISC License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the API examples above

---

**Built with ❤️ using Node.js, Express, and MongoDB**
