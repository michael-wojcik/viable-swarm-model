import { useState, FormEvent } from "react";
import { useAuthStore } from "@/stores/authStore";
import { UserRole } from "@/shared/types";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const setAuth = useAuthStore((s) => s.setAuth);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setAuth("dummy-token", {
      id: "1",
      email,
      name: "User",
      role: UserRole.DISPATCHER,
    });
  };

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Log In</button>
      </form>
    </div>
  );
}
