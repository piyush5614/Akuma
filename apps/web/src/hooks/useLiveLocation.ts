import { useEffect, useState } from "react";

export type LiveLocation = { lat: number; lng: number; source: "live" | "fallback" };

const FALLBACK_LOCATION: LiveLocation = { lat: 18.52, lng: 73.86, source: "fallback" };

export function useLiveLocation() {
  const [location, setLocation] = useState<LiveLocation>({ ...FALLBACK_LOCATION });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!navigator.geolocation) {
      setError("Location is not supported; showing Maharashtra demo location.");
      setLoading(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({ lat: position.coords.latitude, lng: position.coords.longitude, source: "live" });
        setLoading(false);
      },
      () => {
        setError("Location permission was not granted; showing Maharashtra demo location.");
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
    );
  }, []);

  return { location, loading, error };
}
