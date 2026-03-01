import { useState, useRef, useEffect } from "react";
import { searchLocations } from "../services/api";
import type { Location } from "../types/trip";
import "./LocationInput.css";

interface LocationInputProps {
  label: string;
  placeholder?: string;
  onSelect: (location: Location) => void;
}

export default function LocationInput({
  label,
  placeholder,
  onSelect,
}: LocationInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Location[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<Location | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleChange(value: string) {
    setQuery(value);
    setSelected(null);

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (value.length < 3) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      const locations = await searchLocations(value);
      setResults(locations);
      setIsOpen(locations.length > 0);
    }, 350);
  }

  function handleSelect(location: Location) {
    setSelected(location);
    setQuery(location.display_name);
    setIsOpen(false);
    onSelect(location);
  }

  return (
    <div className="location-input" ref={containerRef}>
      <label className="location-input__label">{label}</label>
      <input
        type="text"
        className={`location-input__field ${selected ? "location-input__field--selected" : ""}`}
        placeholder={placeholder}
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => results.length > 0 && setIsOpen(true)}
      />
      {isOpen && (
        <ul className="location-input__dropdown">
          {results.map((loc, i) => (
            <li
              key={`${loc.lat}-${loc.lon}-${i}`}
              className="location-input__option"
              onClick={() => handleSelect(loc)}
            >
              {loc.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
