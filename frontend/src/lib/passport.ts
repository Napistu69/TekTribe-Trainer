import { Auth } from '@imtbl/auth';

let authInstance: Auth | null = null;

/**
 * Initialize the Immutable Passport Auth instance.
 * Must be called once at app startup.
 */
export function initPassport(clientId: string, redirectUri: string) {
  authInstance = new Auth({
    clientId,
    redirectUri,
    scope: 'openid profile email offline_access transact',
  });
}

/**
 * Get the Auth instance. Throws if not initialized.
 */
export function getAuth(): Auth {
  if (!authInstance) {
    throw new Error('Passport not initialized. Call initPassport() first.');
  }
  return authInstance;
}

/**
 * Trigger the Passport login flow (popup-based).
 * Returns the user object on success.
 */
export async function loginWithPassport() {
  const auth = getAuth();
  const user = await auth.login();
  return user;
}

/**
 * Get the currently authenticated user.
 */
export async function getPassportUser() {
  const auth = getAuth();
  return await auth.getUser();
}

/**
 * Log out of Passport.
 */
export async function logoutPassport() {
  const auth = getAuth();
  await auth.logout();
}

/**
 * Check if a user is currently logged in to Passport.
 */
export async function isPassportLoggedIn(): Promise<boolean> {
  try {
    const user = await getPassportUser();
    return !!user;
  } catch {
    return false;
  }
}

/**
 * Extract email from Passport user profile.
 */
export function getEmailFromUser(user: any): string | null {
  return user?.profile?.email || null;
}

/**
 * Extract wallet address from Passport user.
 */
export function getWalletAddressFromUser(user: any): string | null {
  return user?.zkEvm?.ethAddress || null;
}

/**
 * Extract the ID token (used as passport_proof for backend).
 */
export function getIdToken(user: any): string | null {
  return user?.idToken || null;
}
