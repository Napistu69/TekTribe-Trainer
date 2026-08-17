import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getEmailFromUser,
  getIdToken,
  getWalletAddressFromUser,
  loginWithPassport,
} from '../../lib/passport';
import { useAuthStore } from '../../stores/authStore';

export function LoginScreen() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      // 1. Trigger Passport login (popup with email + OTP)
      const passportUser = await loginWithPassport();

      // 2. Extract user data
      const email = getEmailFromUser(passportUser);
      const walletAddress = getWalletAddressFromUser(passportUser);
      const idToken = getIdToken(passportUser);

      if (!email) {
        throw new Error('Email not provided by Passport');
      }

      // 3. Send to backend for session creation
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/auth/login`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            passport_proof: idToken || 'passport_unverified',
            wallet_address: walletAddress || '',
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();

      // 4. Store auth state
      setAuth({
        userId: data.user_id,
        sessionToken: data.session_token,
        userEmail: email,
        walletAddress: walletAddress || '',
        isNewUser: data.is_new_user,
        lockdownActive: data.lockdown_state?.is_active ?? true,
      });

      // 5. Navigate to Hatchery
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
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
