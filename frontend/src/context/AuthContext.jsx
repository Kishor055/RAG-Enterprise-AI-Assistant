import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const DEMO_USERS = {
  admin: {
    email: "admin@enterprise.ai",
    full_name: "Enterprise Admin",
    role: "Admin",
    token: "demo_admin_token"
  },
  manager: {
    email: "manager@enterprise.ai",
    full_name: "Knowledge Manager",
    role: "Knowledge Manager",
    token: "demo_manager_token"
  },
  employee: {
    email: "employee@enterprise.ai",
    full_name: "Standard Employee",
    role: "Standard User",
    token: "demo_employee_token"
  }
};

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(DEMO_USERS.admin);

  const switchRole = (roleKey) => {
    if (DEMO_USERS[roleKey]) {
      setCurrentUser(DEMO_USERS[roleKey]);
    }
  };

  return (
    <AuthContext.Provider value={{ currentUser, setCurrentUser, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
