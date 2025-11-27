export interface Role {
  name: string;
  permissions: Set<string>;
}

export class RoleBasedAccessControl {
  private roles: Map<string, Role> = new Map();
  private userRoles: Map<string, Set<string>> = new Map();

  createRole(roleName: string, permissions: string[]): void {
    this.roles.set(roleName, {
      name: roleName,
      permissions: new Set(permissions)
    });
  }

  assignRole(userId: string, roleName: string): void {
    if (!this.roles.has(roleName)) {
      throw new Error(`Role ${roleName} does not exist`);
    }
    if (!this.userRoles.has(userId)) {
      this.userRoles.set(userId, new Set());
    }
    this.userRoles.get(userId)!.add(roleName);
  }

  hasPermission(userId: string, permission: string): boolean {
    const userRoleSet = this.userRoles.get(userId);
    if (!userRoleSet) {
      return false;
    }
    for (const roleName of userRoleSet) {
      const role = this.roles.get(roleName);
      if (role && role.permissions.has(permission)) {
        return true;
      }
    }
    return false;
  }

  revokeRole(userId: string, roleName: string): void {
    const userRoleSet = this.userRoles.get(userId);
    if (userRoleSet) {
      userRoleSet.delete(roleName);
    }
  }

  getRoles(userId: string): string[] {
    const userRoleSet = this.userRoles.get(userId);
    return userRoleSet ? Array.from(userRoleSet) : [];
  }
}

