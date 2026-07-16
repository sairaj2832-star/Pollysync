import { createContext, useContext, useState, useEffect } from "react";
import { getDistricts } from "../lib/api";

const DistrictContext = createContext(null);

export function DistrictProvider({ children }) {
  const [districts, setDistricts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDistricts();
  }, []);

  async function fetchDistricts() {
    try {
      setLoading(true);
      setError(null);
      const data = await getDistricts();
      setDistricts(data);
    } catch (err) {
      console.error("Failed to fetch districts:", err);
      setError(err.message || "Failed to load districts");
    } finally {
      setLoading(false);
    }
  }

  function getDistrictBySlug(slug) {
    return districts.find((d) => d.slug === slug) || null;
  }

  function getDistrictByName(name) {
    return districts.find(
      (d) => d.name.toLowerCase() === name.toLowerCase()
    ) || null;
  }

  return (
    <DistrictContext.Provider
      value={{
        districts,
        loading,
        error,
        getDistrictBySlug,
        getDistrictByName,
        refreshDistricts: fetchDistricts,
      }}
    >
      {children}
    </DistrictContext.Provider>
  );
}

export function useDistricts() {
  const context = useContext(DistrictContext);
  if (!context) {
    throw new Error("useDistricts must be used within a DistrictProvider");
  }
  return context;
}
