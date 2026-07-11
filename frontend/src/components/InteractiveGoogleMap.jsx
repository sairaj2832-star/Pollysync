import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { searchLocations } from "../lib/location";

export default function InteractiveGoogleMap({
  center = { lat: 19.9975, lng: 73.7898 },
  zoom = 12,
  onLocationSelect,
  selectedAddress = "",
  onUseCurrentLocation,
  showSearch = true,
}) {
  const mapRef = useRef(null);
  const leafletMapRef = useRef(null);
  const leafletMarkerRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");

  useEffect(() => {
    if (!mapRef.current) return;

    if (!leafletMapRef.current) {
      // Clear out any existing elements in the container
      mapRef.current.innerHTML = "";

      const map = L.map(mapRef.current).setView([center.lat, center.lng], zoom);
      
      // Standard colored OpenStreetMap tiles matching the user's screenshot
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);

      // Standard blue Leaflet marker icon matching the user's screenshot
      const blueIcon = L.icon({
        iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });

      const marker = L.marker([center.lat, center.lng], {
        icon: blueIcon,
        draggable: true,
      }).addTo(map);

      marker.bindPopup(selectedAddress || "Selected location").openPopup();

      marker.on("dragend", () => {
        const pos = marker.getLatLng();
        if (onLocationSelect) {
          onLocationSelect({ lat: pos.lat, lng: pos.lng });
        }
      });

      map.on("click", (e) => {
        marker.setLatLng(e.latlng);
        // Keep popup open when marker moves
        marker.openPopup();
        if (onLocationSelect) {
          onLocationSelect({ lat: e.latlng.lat, lng: e.latlng.lng });
        }
      });

      leafletMapRef.current = map;
      leafletMarkerRef.current = marker;
    } else {
      // If coordinates change externally, update map center and marker position
      const currentCenter = leafletMapRef.current.getCenter();
      if (Math.abs(currentCenter.lat - center.lat) > 0.0001 || Math.abs(currentCenter.lng - center.lng) > 0.0001) {
        leafletMapRef.current.panTo([center.lat, center.lng]);
      }
      leafletMarkerRef.current.setLatLng([center.lat, center.lng]);
      leafletMarkerRef.current.bindPopup(selectedAddress || "Selected location");
      leafletMarkerRef.current.openPopup();
    }
  }, [center, zoom, onLocationSelect, selectedAddress]);

  async function handleSearchSubmit(e) {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setSearching(true);
    setSearchError("");
    try {
      const matches = await searchLocations(searchQuery);
      setResults(matches);
    } catch (error) {
      setSearchError(error.message || "Unable to search locations");
    } finally {
      setSearching(false);
    }
  }

  function selectSearchResult(result) {
    setSearchQuery(result.name);
    setResults([]);
    if (onLocationSelect) {
      onLocationSelect({
        lat: result.lat,
        lng: result.lng,
        address: result.name,
      });
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (leafletMapRef.current) {
        leafletMapRef.current.remove();
        leafletMapRef.current = null;
      }
    };
  }, []);

  return (
    <div className="w-full h-full relative rounded-xl overflow-hidden border border-outline-variant bg-surface-container-higher min-h-[300px] flex-1">
      {showSearch && (
        <div className="absolute left-md right-md top-md z-[1000]">
          <form
            onSubmit={handleSearchSubmit}
            className="rounded-xl border border-outline-variant bg-surface/95 backdrop-blur-sm shadow-md p-sm"
          >
            <div className="flex gap-sm">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search location"
                className="flex-1 rounded-lg border border-outline-variant bg-surface px-md py-sm text-body-sm text-on-surface outline-none focus:border-primary"
              />
              <button
                type="submit"
                className="rounded-lg bg-primary px-md py-sm text-label-sm font-semibold text-on-primary"
              >
                Search
              </button>
              {onUseCurrentLocation && (
                <button
                  type="button"
                  onClick={onUseCurrentLocation}
                  className="rounded-lg border border-outline-variant bg-surface-container-high px-md py-sm text-label-sm font-semibold text-primary"
                >
                  Current Location
                </button>
              )}
            </div>
            {searching && <p className="mt-xs text-body-xs text-on-surface-variant">Searching...</p>}
            {searchError && <p className="mt-xs text-body-xs text-error">{searchError}</p>}
            {results.length > 0 && (
              <div className="mt-sm max-h-48 overflow-y-auto rounded-lg border border-outline-variant bg-surface">
                {results.map((result) => (
                  <button
                    key={result.id}
                    type="button"
                    onClick={() => selectSearchResult(result)}
                    className="block w-full border-b border-outline-variant/50 px-md py-sm text-left text-body-sm text-on-surface last:border-b-0 hover:bg-surface-container-high"
                  >
                    {result.name}
                  </button>
                ))}
              </div>
            )}
          </form>
        </div>
      )}
      <div ref={mapRef} className="w-full h-full min-h-[300px]" />
    </div>
  );
}
