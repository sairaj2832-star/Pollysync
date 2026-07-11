import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default function InteractiveGoogleMap({
  center = { lat: 19.9975, lng: 73.7898 },
  zoom = 12,
  onLocationSelect,
}) {
  const mapRef = useRef(null);
  const leafletMapRef = useRef(null);
  const leafletMarkerRef = useRef(null);

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

      // Bind a popup that says "Hello!" and open it by default, matching the user's screenshot
      marker.bindPopup("Hello!").openPopup();

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
      leafletMarkerRef.current.openPopup();
    }
  }, [center, zoom, onLocationSelect]);

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
      <div ref={mapRef} className="w-full h-full min-h-[300px]" />
    </div>
  );
}
