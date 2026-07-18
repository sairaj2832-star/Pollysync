import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../lib/api";

export default function LoginPage() {
  const { user, loading: authLoading, login, loginWithGoogle, isFirebaseConfigured } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (authLoading) {
    return (
      <div className="bg-background min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (user) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!form.email || !form.password) {
      setError("Please enter your email and password.");
      return;
    }
    setBusy(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err, err?.message || "Login failed"));
    } finally {
      setBusy(false);
    }
  }

  async function handleGoogleLogin() {
    setError("");
    setBusy(true);
    try {
      await loginWithGoogle();
      navigate("/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err, err?.message || "Google sign-in failed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-background min-h-screen flex flex-col justify-center items-center p-lg relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary-container/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-container/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-[420px] z-10">
        <div className="text-center mb-xl">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary-container/20 text-primary mb-md">
            <span className="material-symbols-outlined text-[28px] filled">eco</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-xs">Welcome back</h1>
          <p className="font-body-md text-body-md text-on-surface-variant">Sign in to your farm dashboard</p>
        </div>

        <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0_1px_3px_rgba(0,0,0,0.05)] p-xl">
          {error && (
            <div className="mb-md rounded-lg bg-error-container p-3 font-body-sm font-medium text-on-error-container">
              {error}
            </div>
          )}

          {!isFirebaseConfigured && (
            <div className="mb-md rounded-lg bg-secondary-container/30 p-3 font-body-sm text-on-surface-variant">
              Firebase is not configured. Set <code className="font-mono text-xs bg-surface-container-high px-1 rounded">VITE_FIREBASE_*</code> keys in <code className="font-mono text-xs bg-surface-container-high px-1 rounded">frontend/.env</code>.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-lg">
            <div className="flex flex-col gap-xs">
              <label className="font-label-md text-label-md text-on-surface">Email Address</label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">mail</span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-2xl pr-md py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50"
                  placeholder="grower@farm.com"
                  required
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
            </div>

            <div className="flex flex-col gap-xs">
              <div className="flex justify-between items-center">
                <label className="font-label-md text-label-md text-on-surface">Password</label>
                <span className="font-label-sm text-label-sm text-primary hover:text-primary-fixed-dim transition-colors cursor-pointer">
                  Forgot?
                </span>
              </div>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">lock</span>
                <input
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-2xl pr-2xl py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50"
                  placeholder="••••••••"
                  required
                  type={showPassword ? "text" : "password"}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface transition-colors"
                  tabIndex={-1}
                >
                  <span className="material-symbols-outlined text-[20px]">{showPassword ? "visibility_off" : "visibility"}</span>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={busy}
              className="w-full bg-primary hover:brightness-90 text-on-primary font-label-md text-label-md py-[12px] rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-sm"
            >
              {busy ? (
                <span className="flex items-center gap-sm">
                  <span className="w-4 h-4 border-2 border-on-primary/30 border-t-on-primary rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : (
                <>
                  Sign In
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </>
              )}
            </button>
          </form>

          <div className="relative my-lg flex items-center">
            <div className="flex-grow border-t border-outline-variant/30" />
            <span className="flex-shrink-0 mx-md font-label-sm text-label-sm text-on-surface-variant">Or continue with</span>
            <div className="flex-grow border-t border-outline-variant/30" />
          </div>

          <button
            type="button"
            disabled={busy || !isFirebaseConfigured}
            onClick={handleGoogleLogin}
            className="w-full bg-surface border border-outline-variant text-on-surface font-label-md text-label-md py-[12px] rounded-lg hover:bg-surface-container-low active:bg-surface-container transition-colors duration-150 flex items-center justify-center gap-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg fill="none" height="18" viewBox="0 0 24 24" width="18" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Continue with Google
          </button>
        </div>

        <div className="mt-xl text-center space-y-md">
          <p className="font-body-md text-body-md text-on-surface-variant">
            Don&apos;t have an account?{" "}
            <Link to="/register" className="text-primary font-label-md hover:underline hover:text-primary-fixed-dim transition-colors">
              Register
            </Link>
          </p>
          <Link to="/" className="inline-flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface transition-colors">
            <span className="material-symbols-outlined text-[16px]">arrow_back</span>
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
