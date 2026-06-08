import { useState } from "react";

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState("users");

  return (
    <div>
      <h1>Admin Panel</h1>
      <nav>
        <button onClick={() => setActiveTab("users")}>Users</button>
        <button onClick={() => setActiveTab("settings")}>Settings</button>
      </nav>
      <div>Active tab: {activeTab}</div>
    </div>
  );
}
