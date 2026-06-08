import { useState } from "react";

export default function DriverView() {
  const [status, setStatus] = useState("available");

  return (
    <div>
      <h1>Driver View</h1>
      <p>Status: {status}</p>
      <button onClick={() => setStatus("available")}>Available</button>
      <button onClick={() => setStatus("busy")}>Busy</button>
    </div>
  );
}
