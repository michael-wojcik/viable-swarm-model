export const SIO_EVENTS = {
  LOCATION_UPDATE: "location_update",
  DRIVER_STATUS_CHANGE: "driver_status_change",
  NEW_DISPATCH: "new_dispatch",
  DISPATCH_UPDATED: "dispatch_updated",
} as const;

export type SIOEvent = (typeof SIO_EVENTS)[keyof typeof SIO_EVENTS];
