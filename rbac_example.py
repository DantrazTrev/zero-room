#!/usr/bin/env python3
"""
Simple RBAC Example using ADP
==============================

This example demonstrates how Role-Based Access Control
emerges from pure logical principles.
"""

from adp.rbac import (
    ADPRBACProtocol,
    PermissionType,
    ResourceType,
    PolicyDecision
)


def main():
    print("=" * 60)
    print("ADP-RBAC: Simple Example")
    print("=" * 60)
    
    # Initialize protocol
    print("\n[1] Initializing ADP-RBAC Protocol...")
    protocol = ADPRBACProtocol()
    print("    ✓ Protocol initialized with logical foundations")
    
    # Register users
    print("\n[2] Registering Users with Roles:")
    users = [
        ("alice", "admin", "Administrator"),
        ("bob", "user", "Regular User"),
        ("charlie", "viewer", "Read-only User")
    ]
    
    sessions = {}
    for user_id, role, desc in users:
        entity = protocol.register_user(user_id, role)
        print(f"    ✓ {user_id}: {desc} (role: {role})")
        
        # Authenticate
        success, token = protocol.authenticate_user(user_id)
        if success:
            sessions[user_id] = token
    
    # Test permissions
    print("\n[3] Testing Permission Checks:")
    
    test_cases = [
        ("alice", PermissionType.CREATE, "user:new_user", ResourceType.USER,
         "Admin creating a user"),
        ("alice", PermissionType.DELETE, "data:sensitive", ResourceType.DATA,
         "Admin deleting data"),
        ("bob", PermissionType.READ, "data:public", ResourceType.DATA,
         "User reading data"),
        ("bob", PermissionType.DELETE, "data:sensitive", ResourceType.DATA,
         "User trying to delete (should fail)"),
        ("charlie", PermissionType.READ, "data:public", ResourceType.DATA,
         "Viewer reading data"),
        ("charlie", PermissionType.UPDATE, "data:article", ResourceType.DATA,
         "Viewer trying to update (should fail)")
    ]
    
    print()
    for user, action, resource, res_type, description in test_cases:
        token = sessions.get(user)
        if not token:
            continue
            
        response = protocol.check_permission(
            token, action, resource, res_type
        )
        
        icon = "✓" if response.decision == PolicyDecision.PERMIT else "✗"
        print(f"    {icon} {description}")
        print(f"       → Decision: {response.decision.value}")
        if response.advice:
            print(f"       → Advice: {response.advice[0]}")
    
    # Show logical principles
    print("\n[4] Logical Principles at Work:")
    print("    • SHARED: Role definitions are universal")
    print("    • SEPARATE: Role assignments are entity-specific")
    print("    • Authentication: Proves exclusive knowledge")
    print("    • Authorization: Logical evaluation of permissions")
    
    # Show statistics
    print("\n[5] Protocol Statistics:")
    stats = protocol.get_statistics()
    print(f"    • Registered entities: {stats['registered_entities']}")
    print(f"    • Active sessions: {stats['active_sessions']}")
    print(f"    • Total evaluations: {stats['total_evaluations']}")
    if stats['total_evaluations'] > 0:
        print(f"    • Permit rate: {stats['permit_rate']:.0%}")
        print(f"    • Deny rate: {stats['deny_rate']:.0%}")
    
    print("\n" + "=" * 60)
    print("Conclusion: Complex RBAC from Simple Logic!")
    print("=" * 60)
    print("\nThis demonstrates that enterprise-grade access control")
    print("can emerge from the fundamental distinction between")
    print("SHARED and SEPARATE knowledge, without cryptography.")


if __name__ == "__main__":
    main()