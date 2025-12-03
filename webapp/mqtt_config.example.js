// Copy this file to `mqtt_config.js` and fill in the values from HiveMQ Cloud.
// Do NOT commit `mqtt_config.js` with real credentials to a public repo.

window.MQTT_CONFIG = {
  // Example WSS URL formats you may receive from HiveMQ Cloud:
  //  - "wss://<cluster-id>.s1.eu.hivemq.cloud:8883/mqtt"
  //  - "wss://<cluster-host>:8883/mqtt"
  WSS_URL: "wss://REPLACE_WITH_YOUR_CLUSTER_HOST:8883/mqtt",

  // HiveMQ username/password (from the credentials page)
  USERNAME: "REPLACE_WITH_USERNAME",
  PASSWORD: "REPLACE_WITH_PASSWORD",

  // Client ID will be auto-generated and persisted by mqtt_client.js
  // Leave this empty or undefined for automatic ID management
  CLIENT_ID: null,

  // Topic to publish emotion events to (adjust if desired)
  TOPIC: "fer/events",

  // QoS used for publishing (0 or 1). HiveMQ Cloud supports QoS 0/1.
  QOS: 1
};

// After filling values, copy to mqtt_config.js (git-ignored) so the app can connect.
