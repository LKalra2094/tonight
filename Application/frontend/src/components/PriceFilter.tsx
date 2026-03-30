interface PriceFilterProps {
  value: string;
  onChange: (value: string) => void;
}

const PRESETS = ["0", "25", "50", "100", "200"];

export default function PriceFilter({ value, onChange }: PriceFilterProps) {
  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === "" || /^\d+$/.test(raw)) {
      onChange(raw);
    }
  };

  return (
    <div className="price-filter">
      <input
        type="text"
        inputMode="numeric"
        value={value}
        onChange={handleInput}
        placeholder="Max price"
        className="price-input"
      />
      <div className="price-presets">
        {PRESETS.map((p) => (
          <button
            key={p}
            className={`price-preset ${value === p ? "active" : ""}`}
            onClick={() => onChange(p)}
          >
            {p === "0" ? "Free" : `$${p}`}
          </button>
        ))}
        <button
          className={`price-preset ${value === "" ? "active" : ""}`}
          onClick={() => onChange("")}
        >
          No limit
        </button>
      </div>
    </div>
  );
}
