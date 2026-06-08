export enum UserRole {
  DISPATCHER = "DISPATCHER",
  ADMIN = "ADMIN",
  DRIVER = "DRIVER",
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}
