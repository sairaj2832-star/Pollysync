const NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org";

function formatAddress(address = {}) {
  const locality =
    address.city ||
    address.town ||
    address.village ||
    address.hamlet ||
    address.suburb ||
    address.county ||
    "";
  const region = address.state_district || address.state || "";
  const country = address.country || "";

  return [locality, region, country].filter(Boolean).join(", ");
}

export async function reverseGeocode(lat, lng) {
  const url = new URL(`${NOMINATIM_BASE_URL}/reverse`);
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("lat", String(lat));
  url.searchParams.set("lon", String(lng));
  url.searchParams.set("zoom", "18");
  url.searchParams.set("addressdetails", "1");

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Unable to reverse geocode location");
  }

  const data = await response.json();
  return {
    address: formatAddress(data.address) || data.display_name || "Selected location",
    raw: data,
  };
}

export async function searchLocations(query) {
  if (!query?.trim()) {
    return [];
  }

  const url = new URL(`${NOMINATIM_BASE_URL}/search`);
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("q", query.trim());
  url.searchParams.set("limit", "5");
  url.searchParams.set("addressdetails", "1");

  const response = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Unable to search locations");
  }

  const data = await response.json();
  return data.map((item) => ({
    id: item.place_id,
    name: formatAddress(item.address) || item.display_name,
    lat: Number(item.lat),
    lng: Number(item.lon),
  }));
}
