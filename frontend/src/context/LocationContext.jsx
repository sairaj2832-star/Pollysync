import { createContext, useContext, useEffect, useRef, useState } from "react";
import { reverseGeocode } from "../lib/location";

const LocationContext = createContext(null);

const LOCATION_STORAGE_KEY = "pollisync-preferred-location";
const DEFAULT_LOCATION = {
  lat: 19.9975,
  lng: 73.7898,
  address: "Nashik, Maharashtra, India",
  source: "default",
};

function readStoredLocation() {
  if (typeof window === "undefined") {
    return null;
  }

  const stored = window.localStorage.getItem(LOCATION_STORAGE_KEY);
  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored);
  } catch {
    window.localStorage.removeItem(LOCATION_STORAGE_KEY);
    return null;
  }
}

export function LocationProvider({ children }) {
  const [location, setLocation] = useState(() => readStoredLocation() || DEFAULT_LOCATION);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [locationError, setLocationError] = useState("");
  const hasRequestedInitialLocation = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return undefined;
    }

    window.localStorage.setItem(LOCATION_STORAGE_KEY, JSON.stringify(location));

    const clearStoredLocation = () => {
      window.localStorage.removeItem(LOCATION_STORAGE_KEY);
    };

    window.addEventListener("beforeunload", clearStoredLocation);
    return () => {
      window.removeEventListener("beforeunload", clearStoredLocation);
    };
  }, [location]);

  async function setPreferredLocation(coords, source = "manual", providedAddress = "") {
    const nextLat = Number(coords.lat);
    const nextLng = Number(coords.lng);

    setLoadingLocation(true);
    setLocationError("");

    try {
      const geocoded =
        providedAddress?.trim()
          ? { address: providedAddress.trim() }
          : await reverseGeocode(nextLat, nextLng);

      const nextLocation = {
        lat: nextLat,
        lng: nextLng,
        address: geocoded.address,
        source,
      };

      setLocation(nextLocation);
      return nextLocation;
    } catch (error) {
      const fallbackLocation = {
        lat: nextLat,
        lng: nextLng,
        address: providedAddress?.trim() || "Selected location",
        source,
      };
      setLocation(fallbackLocation);
      setLocationError(error.message || "Unable to determine address");
      return fallbackLocation;
    } finally {
      setLoadingLocation(false);
    }
  }

  function requestCurrentLocation(source = "gps") {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        const error = new Error("Geolocation is not supported by your browser");
        setLocationError(error.message);
        reject(error);
        return;
      }

      setLoadingLocation(true);
      setLocationError("");

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const result = await setPreferredLocation(
              {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
              },
              source
            );
            resolve(result);
          } catch (error) {
            reject(error);
          }
        },
        (error) => {
          setLoadingLocation(false);
          setLocationError(error.message || "Failed to access current location");
          reject(error);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    });
  }

  useEffect(() => {
    if (hasRequestedInitialLocation.current) {
      return;
    }

    hasRequestedInitialLocation.current = true;
    requestCurrentLocation("initial").catch(() => {});
  }, []);

  return (
    <LocationContext.Provider
      value={{
        location,
        loadingLocation,
        locationError,
        setPreferredLocation,
        requestCurrentLocation,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error("useLocation must be used within a LocationProvider");
  }
  return context;
}
