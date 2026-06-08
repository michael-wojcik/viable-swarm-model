import { useQuery } from "@apollo/client";
import { DISPATCHES } from "@/graphql/queries";

interface Dispatch {
  id: string;
  status: string;
  destination?: string;
}

interface DispatchesData {
  dispatches: Dispatch[];
}

export default function DispatcherDashboard() {
  const { data, loading } = useQuery<DispatchesData>(DISPATCHES);

  if (loading) return <div>Loading dispatches...</div>;

  return (
    <div>
      <h1>Dispatcher Dashboard</h1>
      <ul>
        {data?.dispatches.map((d) => (
          <li key={d.id}>{d.destination ?? d.id}</li>
        ))}
      </ul>
    </div>
  );
}
