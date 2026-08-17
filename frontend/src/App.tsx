import { registerServiceWorker } from './service-worker-registration'

function App() {
  // Initialize service worker
  registerServiceWorker()

  return (
    <div className="app-shell">
      <div className="loading-screen">
        <h1>TekTribe Trainer</h1>
        <p>Loading the Hatchery...</p>
      </div>
    </div>
  )
}

export default App
