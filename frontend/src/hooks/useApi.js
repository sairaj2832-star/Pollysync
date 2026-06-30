import { useState } from "react";

export default function useApi(apiFunc) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function execute(...args) {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFunc(...args);
      setData(result);
      return result;
    } catch (err) {
      const message = err?.response?.data?.detail || err.message || "An error occurred";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setData(null);
    setError(null);
    setLoading(false);
  }

  return { data, loading, error, execute, reset };
}
