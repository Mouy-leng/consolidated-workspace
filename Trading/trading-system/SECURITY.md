# 🔐 Security Guidelines

## Critical Security Rules

### ❌ NEVER COMMIT:
- Real trading credentials
- API keys or tokens
- SSH private keys
- Database passwords
- Any `.env` files with real data

### ✅ ALWAYS USE:
- Environment variables for credentials
- `.env.template` for examples
- Secure backup files outside repository
- Strong passwords and 2FA

## Credential Management

### Secure Files (Outside Repository):
- `.env.fbs.secure` - FBS trading credentials
- `.env.backup.secure` - All real credentials

### Template Files (Safe to Commit):
- `.env.template` - Example configuration
- `.env.example` - Microservice examples

## Trading Safety

### FBS Live Account Protection:
1. **Change password immediately** after any exposure
2. **Enable 2FA** on FBS account
3. **Monitor account activity** regularly
4. **Use stop losses** on all trades
5. **Set daily loss limits**

### VPS Security:
1. Use SSH keys instead of passwords
2. Disable root login
3. Enable firewall
4. Regular security updates
5. Monitor access logs

## Emergency Procedures

### If Credentials Are Compromised:
1. Change all passwords immediately
2. Revoke API keys
3. Check account activity
4. Enable additional security measures
5. Rotate SSH keys