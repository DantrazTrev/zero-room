# ADP-RBAC Usage Guide

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/adp-rbac
cd adp-rbac

# No external dependencies required!
python3 --version  # Ensure Python 3.8+

# Run tests
python3 -m adp.tests.test_adp

# Run RBAC demo
python3 -m adp.rbac_demo
```

### Basic Usage

```python
from adp.rbac import ADPRBACProtocol

# Initialize the protocol
protocol = ADPRBACProtocol()

# Register users with roles
alice = protocol.register_user("alice", "admin")
bob = protocol.register_user("bob", "user")

# Authenticate users
success, alice_token = protocol.authenticate_user("alice")
success, bob_token = protocol.authenticate_user("bob")

# Check permissions
from adp.rbac import PermissionType, ResourceType

response = protocol.check_permission(
    alice_token,
    PermissionType.CREATE,
    "user:new_user",
    ResourceType.USER
)

if response.decision.value == "permit":
    print("Access granted!")
else:
    print(f"Access denied: {response.reason}")
```

## Common Use Cases

### 1. User Management System

```python
class UserManagementSystem:
    """Example user management system using ADP-RBAC."""
    
    def __init__(self):
        self.protocol = ADPRBACProtocol()
        self.users = {}
        
    def create_user(self, admin_token, username, email, role="user"):
        """Create a new user (requires admin privileges)."""
        
        # Check permission
        response = self.protocol.check_permission(
            admin_token,
            PermissionType.CREATE,
            f"user:{username}",
            ResourceType.USER
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot create user: {response.reason}")
            
        # Register user in ADP-RBAC
        entity = self.protocol.register_user(username, role)
        
        # Store user data
        self.users[username] = {
            'email': email,
            'role': role,
            'entity': entity,
            'created_at': time.time()
        }
        
        return username
        
    def update_user(self, session_token, username, updates):
        """Update user information."""
        
        # Check permission
        response = self.protocol.check_permission(
            session_token,
            PermissionType.UPDATE,
            f"user:{username}",
            ResourceType.USER
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot update user: {response.reason}")
            
        # Apply updates
        if username in self.users:
            self.users[username].update(updates)
            
        # Handle obligations
        for obligation in response.obligations:
            if "audit" in obligation.lower():
                self._audit_log(f"User {username} updated")
                
    def delete_user(self, admin_token, username):
        """Delete a user (requires admin privileges)."""
        
        # Check permission
        response = self.protocol.check_permission(
            admin_token,
            PermissionType.DELETE,
            f"user:{username}",
            ResourceType.USER
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot delete user: {response.reason}")
            
        # Delete user
        if username in self.users:
            del self.users[username]
            
    def _audit_log(self, message):
        """Log audit events."""
        print(f"[AUDIT] {time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")
```

### 2. Document Management System

```python
class DocumentManagementSystem:
    """Document management with fine-grained access control."""
    
    def __init__(self):
        self.protocol = ADPRBACProtocol()
        self.documents = {}
        
    def create_document(self, session_token, doc_id, content, 
                       classification="public"):
        """Create a new document."""
        
        # Check permission based on classification
        resource = f"document:{classification}:{doc_id}"
        response = self.protocol.check_permission(
            session_token,
            PermissionType.CREATE,
            resource,
            ResourceType.DATA
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot create document: {response.reason}")
            
        # Get user from session
        session = self.protocol._authenticated_sessions.get(session_token)
        
        # Store document
        self.documents[doc_id] = {
            'content': content,
            'classification': classification,
            'owner': session['user_id'],
            'created_at': time.time(),
            'version': 1,
            'access_log': []
        }
        
        return doc_id
        
    def read_document(self, session_token, doc_id):
        """Read a document."""
        
        if doc_id not in self.documents:
            raise ValueError("Document not found")
            
        doc = self.documents[doc_id]
        resource = f"document:{doc['classification']}:{doc_id}"
        
        # Check permission
        response = self.protocol.check_permission(
            session_token,
            PermissionType.READ,
            resource,
            ResourceType.DATA
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot read document: {response.reason}")
            
        # Log access
        session = self.protocol._authenticated_sessions.get(session_token)
        doc['access_log'].append({
            'user': session['user_id'],
            'action': 'read',
            'timestamp': time.time()
        })
        
        return doc['content']
        
    def update_document(self, session_token, doc_id, new_content):
        """Update a document."""
        
        if doc_id not in self.documents:
            raise ValueError("Document not found")
            
        doc = self.documents[doc_id]
        resource = f"document:{doc['classification']}:{doc_id}"
        
        # Check permission
        session = self.protocol._authenticated_sessions.get(session_token)
        context = {'owner': doc['owner'], 'entity_id': session['user_id']}
        
        response = self.protocol.check_permission(
            session_token,
            PermissionType.UPDATE,
            resource,
            ResourceType.DATA,
            context
        )
        
        if response.decision.value != "permit":
            raise PermissionError(f"Cannot update document: {response.reason}")
            
        # Update document
        doc['content'] = new_content
        doc['version'] += 1
        doc['access_log'].append({
            'user': session['user_id'],
            'action': 'update',
            'version': doc['version'],
            'timestamp': time.time()
        })
        
        return doc['version']
```

### 3. API Access Control

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
protocol = ADPRBACProtocol()

def require_permission(action, resource_type):
    """Decorator for API endpoint access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get session token from header
            token = request.headers.get('X-Session-Token')
            if not token:
                return jsonify({'error': 'No session token'}), 401
                
            # Determine resource from endpoint
            resource = request.path
            
            # Check permission
            response = protocol.check_permission(
                token, action, resource, resource_type
            )
            
            if response.decision.value != "permit":
                return jsonify({
                    'error': 'Access denied',
                    'reason': response.reason,
                    'advice': response.advice
                }), 403
                
            # Add decision to request context
            request.adp_decision = response
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/api/users', methods=['GET'])
@require_permission(PermissionType.READ, ResourceType.USER)
def list_users():
    """List all users."""
    return jsonify({'users': ['alice', 'bob', 'charlie']})

@app.route('/api/users', methods=['POST'])
@require_permission(PermissionType.CREATE, ResourceType.USER)
def create_user():
    """Create a new user."""
    data = request.json
    # Create user logic here
    return jsonify({'status': 'created', 'user': data['username']}), 201

@app.route('/api/users/<username>', methods=['DELETE'])
@require_permission(PermissionType.DELETE, ResourceType.USER)
def delete_user(username):
    """Delete a user."""
    # Handle obligations from decision
    if request.adp_decision.obligations:
        for obligation in request.adp_decision.obligations:
            if "audit" in obligation:
                log_audit_event(f"User {username} deleted")
                
    # Delete user logic here
    return jsonify({'status': 'deleted'}), 200

@app.route('/api/audit', methods=['GET'])
@require_permission(PermissionType.AUDIT, ResourceType.AUDIT_LOG)
def view_audit_logs():
    """View audit logs."""
    token = request.headers.get('X-Session-Token')
    authorized, logs = protocol.audit_access(token, limit=100)
    
    if authorized:
        return jsonify({'logs': logs})
    else:
        return jsonify({'error': 'Audit access denied'}), 403
```

### 4. Dynamic Role Creation

```python
def create_department_roles(protocol, admin_token):
    """Create custom roles for different departments."""
    
    departments = [
        {
            'name': 'finance_analyst',
            'parents': ['user'],
            'permissions': [
                ('READ', ResourceType.DATA, 'finance/*'),
                ('EXECUTE', ResourceType.DATA, 'reports/finance/*'),
                ('READ', ResourceType.AUDIT_LOG, 'finance/*')
            ]
        },
        {
            'name': 'hr_manager',
            'parents': ['user'],
            'permissions': [
                ('CREATE', ResourceType.USER, '*'),
                ('READ', ResourceType.USER, '*'),
                ('UPDATE', ResourceType.USER, '*'),
                ('READ', ResourceType.DATA, 'hr/*')
            ]
        },
        {
            'name': 'security_officer',
            'parents': ['auditor'],
            'permissions': [
                ('READ', ResourceType.AUDIT_LOG, '*'),
                ('AUDIT', ResourceType.SYSTEM, '*'),
                ('READ', ResourceType.USER, '*'),
                ('UPDATE', ResourceType.PERMISSION, 'security/*')
            ]
        }
    ]
    
    for dept in departments:
        # Create permission set
        perm_set = PermissionSet(f"{dept['name']}_permissions")
        
        for perm_type, res_type, pattern in dept['permissions']:
            permission = Permission(
                name=f"{dept['name']}_{perm_type.lower()}_{res_type.value}",
                permission_type=PermissionType[perm_type],
                resource_type=res_type,
                resource_pattern=pattern
            )
            perm_set.add_permission(permission)
            
        # Create role
        success, message = protocol.create_custom_role(
            admin_token,
            dept['name'],
            dept['parents'],
            perm_set
        )
        
        print(f"Created role {dept['name']}: {message}")
```

### 5. Session Management

```python
class SessionManager:
    """Enhanced session management for ADP-RBAC."""
    
    def __init__(self, protocol):
        self.protocol = protocol
        self.session_metadata = {}
        
    def create_session(self, user_id, device_info=None, ip_address=None):
        """Create an enhanced session with metadata."""
        
        # Authenticate user
        success, token = self.protocol.authenticate_user(user_id)
        
        if success:
            # Store metadata
            self.session_metadata[token] = {
                'device': device_info,
                'ip_address': ip_address,
                'created_at': time.time(),
                'last_activity': time.time(),
                'activity_count': 0
            }
            
        return success, token
        
    def validate_session(self, token, ip_address=None):
        """Validate session with additional checks."""
        
        # Check if session exists
        if token not in self.protocol._authenticated_sessions:
            return False, "Invalid session"
            
        # Check metadata
        if token in self.session_metadata:
            metadata = self.session_metadata[token]
            
            # Check IP address if provided
            if ip_address and metadata['ip_address'] != ip_address:
                return False, "IP address mismatch"
                
            # Check session age
            age = time.time() - metadata['created_at']
            if age > 86400:  # 24 hours
                return False, "Session expired"
                
            # Update activity
            metadata['last_activity'] = time.time()
            metadata['activity_count'] += 1
            
        return True, "Valid session"
        
    def revoke_session(self, token):
        """Revoke a session."""
        
        if token in self.protocol._authenticated_sessions:
            del self.protocol._authenticated_sessions[token]
            
        if token in self.session_metadata:
            del self.session_metadata[token]
            
    def get_active_sessions(self, user_id):
        """Get all active sessions for a user."""
        
        sessions = []
        for token, session in self.protocol._authenticated_sessions.items():
            if session['user_id'] == user_id:
                metadata = self.session_metadata.get(token, {})
                sessions.append({
                    'token': token[:8] + '...',  # Partial token for security
                    'created_at': metadata.get('created_at'),
                    'last_activity': metadata.get('last_activity'),
                    'device': metadata.get('device'),
                    'ip_address': metadata.get('ip_address')
                })
                
        return sessions
```

## Advanced Features

### Delegation Chains

```python
def create_delegation_chain(protocol, delegator_token, delegates, role, resource):
    """Create a chain of delegated permissions."""
    
    chain = []
    current_delegator = delegator_token
    
    for delegate in delegates:
        # Check if current delegator can delegate
        response = protocol.check_permission(
            current_delegator,
            PermissionType.DELEGATE,
            resource,
            ResourceType.ROLE
        )
        
        if response.decision.value != "permit":
            print(f"Delegation chain broken at {delegate}")
            break
            
        # Assign role with delegation
        success, message = protocol.assign_role(
            current_delegator,
            delegate,
            role,
            expires_at=time.time() + 3600  # 1 hour delegation
        )
        
        if success:
            chain.append({
                'delegator': current_delegator,
                'delegate': delegate,
                'role': role,
                'timestamp': time.time()
            })
            
            # Authenticate delegate for next iteration
            success, token = protocol.authenticate_user(delegate)
            if success:
                current_delegator = token
                
    return chain
```

### Policy Templates

```python
class PolicyTemplate:
    """Reusable policy templates."""
    
    @staticmethod
    def least_privilege_policy(role_name, allowed_actions, resource_pattern):
        """Create a least privilege policy."""
        perm_set = PermissionSet(f"{role_name}_least_privilege")
        
        for action in allowed_actions:
            perm = Permission(
                name=f"{role_name}_{action.value}",
                permission_type=action,
                resource_type=ResourceType.DATA,
                resource_pattern=resource_pattern,
                conditions={'time_window': lambda t: 9 <= t.hour <= 17}  # Business hours only
            )
            perm_set.add_permission(perm)
            
        return perm_set
        
    @staticmethod
    def temporary_access_policy(role_name, duration_hours=1):
        """Create a temporary access policy."""
        expiry = time.time() + (duration_hours * 3600)
        
        perm_set = PermissionSet(f"{role_name}_temporary")
        perm = Permission(
            name=f"{role_name}_temp_access",
            permission_type=PermissionType.READ,
            resource_type=ResourceType.DATA,
            resource_pattern="*",
            conditions={'expires_at': lambda t: t < expiry}
        )
        perm_set.add_permission(perm)
        
        return perm_set
```

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failures**
   ```python
   # Check if entity is registered
   if not protocol._entities.get(user_id):
       protocol.register_user(user_id, "viewer")
   ```

2. **Permission Denied**
   ```python
   # Check user's roles
   authorized, roles = protocol.get_user_roles(session_token)
   print(f"User roles: {roles}")
   
   # Check what roles would grant access
   # This would be in the advice field of the response
   ```

3. **Session Expiration**
   ```python
   # Clean up expired sessions
   cleaned = protocol.cleanup_sessions(max_age=3600)
   print(f"Cleaned {cleaned} expired sessions")
   ```

4. **Boundary Integrity Issues**
   ```python
   # Check boundary integrity
   from adp import IntegrityChecker
   checker = IntegrityChecker(protocol._adp.logical_boundary)
   intact, reason = checker.check_boundary_integrity(user_id)
   ```

## Performance Tips

1. **Cache Decisions**: Cache permission decisions for frequently accessed resources
2. **Batch Operations**: Process multiple permission checks together
3. **Use Witnesses**: Leverage the witness system for consensus-based decisions
4. **Optimize Hierarchies**: Keep role hierarchies shallow for faster traversal

## Security Best Practices

1. **Regular Audits**: Review access logs regularly
2. **Role Reviews**: Periodically review and update role assignments
3. **Session Management**: Implement session timeouts and IP validation
4. **Principle of Least Privilege**: Grant minimum necessary permissions
5. **Separation of Duties**: Ensure critical operations require multiple roles

## Conclusion

ADP-RBAC provides a powerful, logically-grounded approach to access control that scales from simple applications to enterprise systems. By understanding the fundamental distinction between SHARED and SEPARATE knowledge, you can build secure, verifiable, and maintainable access control systems without the complexity of traditional cryptographic approaches.