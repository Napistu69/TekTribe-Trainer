// Register service worker with auto-update
export function registerServiceWorker() {
  // Skip service worker in dev mode (virtual:pwa-register only works in production build)
  if (!import.meta.env.PROD) {
    return;
  }
  
  import('virtual:pwa-register').then(({ registerSW }) => {
    const updateSW = registerSW({
      onNeedRefresh() {
        if (confirm('New content available. Reload?')) {
          updateSW(true)
        }
      },
      onOfflineReady() {
        // App ready to work offline
      }
    });
  }).catch(() => {
    // Silently fail if PWA module is not available
  });
}
