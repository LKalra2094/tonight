import { useState } from "react";

interface SearchBarProps {
  onSearch: (keyword: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [keyword, setKeyword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = keyword.trim();
    if (trimmed) {
      onSearch(trimmed);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      <input
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="Search SF events (e.g. comedy, live music)"
        disabled={loading}
      />
      <button type="submit" disabled={loading || !keyword.trim()}>
        {loading ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
