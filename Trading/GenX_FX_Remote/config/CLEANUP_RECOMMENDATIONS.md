# A6-9V Repository Cleanup Checklist

## Manual Cleanup Steps:

### 1. Identify Unused Repositories
- Check last commit date (older than 6 months)
- Review repository purpose and relevance
- Check if dependencies exist in other projects

### 2. Archive vs Delete Decision Matrix
**Archive if:**
- Historical value or reference needed
- Part of learning journey documentation
- Contains useful code snippets

**Delete if:**
- Test repositories with no real content
- Duplicate or redundant projects
- Broken projects with no value

### 3. Security Cleanup
- Remove any repositories with exposed secrets
- Check for hardcoded credentials in history
- Verify no sensitive data in commit history

### 4. Organization
- Rename repositories to follow A6-9V naming convention
- Add meaningful descriptions
- Set appropriate visibility (private for sensitive work)
- Add topics/tags for better organization

## A6-9V Naming Convention:
- **Core projects**: a69v-[project-name]
- **Tools/utilities**: a69v-tools-[tool-name]
- **Templates**: a69v-template-[type]
- **Documentation**: a69v-docs-[topic]

## Recommended Actions:
1. Run: gh repo list --json name,pushedAt,description
2. Review output and identify cleanup candidates
3. Use GitHub's archive feature for historical repos
4. Delete truly unnecessary repositories
5. Rename remaining repos to follow convention
