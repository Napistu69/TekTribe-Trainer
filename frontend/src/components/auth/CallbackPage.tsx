import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuth, getEmailFromUser, getIdToken, getWalletAddressFromUser } from '../../lib/passport';
import { useAuthStore } from '../../stores/authStore';

export function CallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const setAuth = useAuthStore((s) => s.setAuth);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const auth = getAuth();
        const passportUser = await auth.loginCallback();
        
        if (!passportUser) {
          throw new Error('Login callback returned no user');
        }

        // Extract user data
        const email = getEmailFromUser(passportUser);
        const walletAddress = getWalletAddressFromUser(passportUser);
        const idToken = getIdToken(passportUser);

        if (!email) {
          throw new Error('Email not provided by Passport');
        }

        // Send to backend for session creation
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

        // Store auth state
        setAuth({
          userId: data.user_id,
          sessionToken: data.session_token,
          userEmail: email,
          walletAddress: walletAddress || '',
          isNewUser: data.is_new_user,
          lockdownActive: data.lockdown_state?.is_active ?? true,
        });

        // Navigate to Hatchery
        navigate('/', { replace: true });
      } catch (err: any) {
        setError(err.message || 'Login callback failed');
      }
    };
    handleCallback();
  }, [navigate, setAuth]);

  if (error) {
    return (
      <div className="callback-error">
        <p>Login failed: {error}</p>
        <button onClick={() => navigate('/login')}>Back to Login</button>
      </div>
    );
  }

  return (
    <div className="callback-loading">
      <p>Completing login...</p>
    </div>
  );
}
