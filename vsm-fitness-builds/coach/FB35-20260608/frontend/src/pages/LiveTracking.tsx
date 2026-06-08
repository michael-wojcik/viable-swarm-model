import { useSubscription } from "@apollo/client";
import { LIVE_LOCATIONS } from "@/graphql/queries";

interface Location {
  driverId: string;
  lat: number;
  lng: number;
  timestamp: string;
}

interface LiveLocationsData {
  liveLocations: Location[];
}

export default function LiveTracking() {
  const { data, loading } = useSubscription<LiveLocationsData>(LIVE_LOCATIONS);

  if (loading) return <div>Connecting to live tracking...</div>;

  return (
    <div>
      <h1>Live Tracking</h1>
      <ul>
        {data?.liveLocations.map((loc, i) => (
          <li key={i}>
            Driver {loc.driverId}: {loc.lat}, {loc.lng}
          </li>
        ))}
      </ul>
    </div>
  );
}
