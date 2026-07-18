import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { getFarms } from "../lib/api";
import { useAuth } from "./AuthContext";

const FarmContext = createContext(null);
const STORAGE_KEY = "selectedFarmId";

export function FarmProvider({ children }) {
  const { user, loading } = useAuth();
  const [farms, setFarms] = useState([]);
  const [selectedFarmId, setSelectedFarmId] = useState(() => localStorage.getItem(STORAGE_KEY) || "");
  const [loadingFarms, setLoadingFarms] = useState(true);

  const refreshFarms = useCallback(async () => {
    setLoadingFarms(true);
    try {
      const data = await getFarms();
      const nextFarms = Array.isArray(data) ? data : [];
      setFarms(nextFarms);
      setSelectedFarmId((current) => {
        const exists = nextFarms.some((farm) => String(farm.id) === String(current));
        const fallback = nextFarms.find((farm) => farm.is_default) || nextFarms[0];
        const nextId = exists ? String(current) : fallback ? String(fallback.id) : "";
        if (nextId) localStorage.setItem(STORAGE_KEY, nextId);
        else localStorage.removeItem(STORAGE_KEY);
        return nextId;
      });
      return nextFarms;
    } catch (error) {
      setFarms([]);
      return [];
    } finally {
      setLoadingFarms(false);
    }
  }, []);

  useEffect(() => {
    if (loading) return;
    if (!user) {
      setFarms([]);
      setSelectedFarmId("");
      localStorage.removeItem(STORAGE_KEY);
      setLoadingFarms(false);
      return;
    }
    refreshFarms();
  }, [loading, refreshFarms, user]);

  const selectFarm = useCallback((id) => {
    const nextId = id == null ? "" : String(id);
    setSelectedFarmId(nextId);
    if (nextId) localStorage.setItem(STORAGE_KEY, nextId);
  }, []);

  const selectedFarm = farms.find((farm) => String(farm.id) === String(selectedFarmId)) || null;

  return (
    <FarmContext.Provider value={{ farms, selectedFarm, selectedFarmId, loadingFarms, selectFarm, refreshFarms }}>
      {children}
    </FarmContext.Provider>
  );
}

export function useFarm() {
  const context = useContext(FarmContext);
  if (!context) throw new Error("useFarm must be used within a FarmProvider");
  return context;
}
