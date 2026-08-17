import { useState } from 'react';
import { loginWithPassport } from '../../lib/passport';

export function LoginScreen() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      // Redirect to Passport login page
      await loginWithPassport();
      // No need to handle return - page will redirect
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-logo">
          <div className="logo-circle" />
          <h1>TekTribe Trainer</h1>
          <p className="tagline">Bond with the Past, Explore the Future</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="btn-primary"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading ? 'Connecting...' : 'Sign In'}
        </button>

        <p className="login-hint">
          Sign in with email. No wallet setup required.
        </p>
      </div>
    </div>
  );
}
