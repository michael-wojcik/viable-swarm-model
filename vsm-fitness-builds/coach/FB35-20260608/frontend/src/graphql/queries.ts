import { gql } from "@apollo/client";

export const DISPATCHES = gql`
  query Dispatches {
    dispatches {
      id
      status
      driver {
        id
        name
      }
      destination
    }
  }
`;

export const LIVE_LOCATIONS = gql`
  subscription LiveLocations {
    liveLocations {
      driverId
      lat
      lng
      timestamp
    }
  }
`;
