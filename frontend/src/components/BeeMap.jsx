import { useEffect, useRef } from "react";

export default function BeeMap({ center = [20, 78], occurrences = [], zoom = 8 }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    let leafletL, map;

    async function init() {
      const L = await import("leaflet");
      leafletL = L;

      if (!mapInstance.current && mapRef.current) {
        map = L.map(mapRef.current).setView(center, zoom);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "&copy; OpenStreetMap contributors",
          maxZoom: 18,
        }).addTo(map);
        mapInstance.current = map;
      }
    }

    init();

    return () => {
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];
    };
  }, [center, zoom]);

  useEffect(() => {
    async function addMarkers() {
      const L = await import("leaflet");
      markersRef.current.forEach((m) => m.remove());
      markersRef.current = [];

      if (!mapInstance.current) return;

      const redIcon = L.icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-red.png",
        shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
      });

      occurrences.forEach((occ) => {
        const marker = L.marker([occ.lat, occ.lng], { icon: redIcon })
          .addTo(mapInstance.current)
          .bindPopup(`<b>${occ.species}</b>`);
        markersRef.current.push(marker);
      });

      if (occurrences.length > 0) {
        const group = L.featureGroup(markersRef.current);
        mapInstance.current.fitBounds(group.getBounds().pad(0.1));
      }
    }

    addMarkers();
  }, [occurrences]);

  return (
    <div className="bg-surface border border-outline-variant rounded-xl overflow-hidden shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div ref={mapRef} className="h-72 w-full" />
    </div>
  );
}
