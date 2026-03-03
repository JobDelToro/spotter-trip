import { useState } from "react";
import TripForm from "./components/TripForm";
import TripMap from "./components/TripMap";
import TripSummary from "./components/TripSummary";
import ELDLogs from "./components/ELDLogs";
import type { TripRequest, TripResult } from "./types/trip";
import { planTrip } from "./services/api";
import "./App.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TripResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handlePlanTrip(data: TripRequest) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const tripResult = await planTrip(data);
      setResult(tripResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Spotter Trip Planner</h1>
        <p>Plan your route with HOS-compliant stops and ELD logs</p>
      </header>
      <main className="app-main">
        <aside className="app-sidebar">
          <TripForm onSubmit={handlePlanTrip} loading={loading} />
          {error && <div className="app-error">{error}</div>}
        </aside>
        <section className="app-content">
          {result ? (
            <>
              <TripMap trip={result} />
              <TripSummary trip={result} />
              <ELDLogs logs={result.eld_logs} />
            </>
          ) : (
            <div className="app-placeholder">
              Enter trip details and click "Plan Trip" to see your route.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
