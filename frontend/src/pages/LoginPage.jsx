import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { token, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (token) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="subtle-gradient-bg min-h-screen flex flex-col justify-center items-center p-md sm:p-gutter relative overflow-hidden"
      style={{
        background: "linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(254, 166, 25, 0.05) 100%), #fff8f5"
      }}
    >
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-primary-container/20 blur-3xl opacity-50" />
        <div className="absolute top-1/2 -right-40 w-[30rem] h-[30rem] rounded-full bg-secondary-container/20 blur-3xl opacity-30" />
      </div>

      <div className="w-full max-w-[420px] z-10">
        <div className="text-center mb-xl">
          <h1 className="font-display text-display text-primary flex items-center justify-center gap-sm">
            <span className="material-symbols-outlined text-4xl filled">eco</span>
            PolliSync
          </h1>
        </div>

        <div
          className="rounded-xl p-lg sm:p-xl w-full"
          style={{
            background: "rgba(255, 248, 245, 0.9)",
            backdropFilter: "blur(12px)",
            WebkitBackdropFilter: "blur(12px)",
            border: "1px solid rgba(226, 232, 240, 0.5)",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)"
          }}
        >
          <div className="mb-xl text-center">
            <h2 className="font-headline-lg text-headline-lg text-on-surface mb-sm">Welcome back</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">Sign in to your farm dashboard</p>
          </div>

          {error && (
            <div className="mb-md rounded-lg bg-error-container p-3 font-body-sm font-medium text-on-error-container">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-md">
            <div>
              <label className="block font-label-md text-label-md text-on-surface mb-xs">Email Address</label>
              <div className="relative flex items-center rounded-lg border border-outline-variant bg-surface transition-shadow duration-200 focus-within:border-primary focus-within:shadow-[0_0_0_2px_rgba(16,185,129,0.2)]">
                <span className="material-symbols-outlined absolute left-md text-on-surface-variant text-[20px]">mail</span>
                <input
                  className="w-full pl-[48px] pr-md py-sm bg-transparent border-none focus:ring-0 font-body-md text-body-md text-on-surface rounded-lg placeholder:text-on-surface-variant/50"
                  placeholder="grower@farm.com"
                  required
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-xs">
                <label className="block font-label-md text-label-md text-on-surface">Password</label>
                <span className="font-label-sm text-label-sm text-primary hover:text-primary-fixed-dim transition-colors cursor-pointer">
                  Forgot?
                </span>
              </div>
              <div className="relative flex items-center rounded-lg border border-outline-variant bg-surface transition-shadow duration-200 focus-within:border-primary focus-within:shadow-[0_0_0_2px_rgba(16,185,129,0.2)]">
                <span className="material-symbols-outlined absolute left-md text-on-surface-variant text-[20px]">lock</span>
                <input
                  className="w-full pl-[48px] pr-[48px] py-sm bg-transparent border-none focus:ring-0 font-body-md text-body-md text-on-surface rounded-lg placeholder:text-on-surface-variant/50"
                  placeholder="••••••••"
                  required
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
              </div>
            </div>

            <div className="flex items-center mt-md mb-lg">
              <input
                className="rounded border-outline-variant text-primary focus:ring-primary bg-surface w-4 h-4 cursor-pointer"
                id="remember"
                type="checkbox"
              />
              <label className="ml-sm font-body-sm text-body-sm text-on-surface-variant cursor-pointer" htmlFor="remember">
                Remember me for 30 days
              </label>
            </div>

            <button
              type="submit"
              disabled={busy}
              className="w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-[12px] rounded-lg shadow-sm hover:opacity-90 active:scale-[0.98] transition-all duration-150 flex items-center justify-center gap-sm"
            >
              {busy ? "Signing in..." : "Sign In"}
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </form>

          <div className="relative my-lg flex items-center">
            <div className="flex-grow border-t border-outline-variant/50" />
            <span className="flex-shrink-0 mx-md font-label-sm text-label-sm text-on-surface-variant">Or continue with</span>
            <div className="flex-grow border-t border-outline-variant/50" />
          </div>

          <button
            type="button"
            className="w-full bg-surface border border-outline-variant text-on-surface font-label-md text-label-md py-[12px] rounded-lg hover:bg-surface-container-low active:bg-surface-container transition-colors duration-150 flex items-center justify-center gap-sm"
          >
            <svg fill="none" height="18" viewBox="0 0 24 24" width="18" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
            </svg>
            Google
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
