import { useEffect, useState } from "react";
import { api } from "./api.js";

export function useResourceList(resource, params) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .list(resource, params)
      .then((rows) => {
        if (!cancelled) setData(rows);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource, JSON.stringify(params)]);

  return { data, loading, error };
}

export function useFieldOptions() {
  const { data } = useResourceList("fields");
  return data.map((f) => ({ value: f.id, label: f.name }));
}

export function useMachineOptions() {
  const { data } = useResourceList("machines");
  return data.map((m) => ({ value: m.id, label: m.name }));
}

export function currentYear() {
  return new Date().getFullYear();
}

export function yearOptions(span = 8) {
  const y = currentYear();
  const years = [];
  for (let i = 0; i < span; i++) years.push(y - i);
  return years;
}
