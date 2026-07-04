import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const LOCATIONS = [
  "Nashik", "Punjab", "Haryana", "Gujarat", "Madhya Pradesh",
  "Maharashtra", "Rajasthan", "Uttar Pradesh", "Bihar", "Karnataka",
  "Andhra Pradesh", "Telangana", "Odisha", "West Bengal", "Tamil Nadu",
  "Kerala", "Assam", "Jharkhand", "Chhattisgarh", "Uttarakhand",
];

export default function RegisterPage() {
  const { token, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "", fullName: "", confirmPassword: "", farmName: "", location: "" });
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (token) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    if (step === 1) {
      if (!form.fullName || !form.email || !form.password) {
        setError("Please fill all fields");
        return;
      }
      if (form.password !== form.confirmPassword) {
        setError("Passwords do not match");
        return;
      }
      setError("");
      setStep(2);
      return;
    }
    setError("");
    setBusy(true);
    try {
      await register(form.email, form.password, form.fullName);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  const inputClass = "w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-2xl pr-md py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50";

  return (
    <div className="bg-background min-h-screen flex items-center justify-center p-lg md:p-2xl relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary-container/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-container/10 rounded-full blur-3xl pointer-events-none" />

      <main className="w-full max-w-[480px] bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0_1px_3px_rgba(0,0,0,0.05)] p-xl relative z-10">
        <div className="text-center mb-xl">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary-container/20 text-primary mb-md">
            <span className="material-symbols-outlined text-[28px] filled">agriculture</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-xs hidden md:block">
            Start Your Pollination Journey
          </h1>
          <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface mb-xs md:hidden">
            Start Your Pollination Journey
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Create your PolliSync account to begin.
          </p>
        </div>

        <div className="flex items-center justify-between mb-2xl relative">
          <div className="absolute left-0 top-1/2 w-full h-[2px] bg-surface-variant -translate-y-1/2 z-0" />
          <div className="relative z-10 flex flex-col items-center gap-sm bg-surface-container-lowest px-sm">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-label-sm text-label-sm shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)] ${
              step >= 1 ? "bg-primary text-on-primary" : "bg-surface-variant text-on-surface-variant border border-outline-variant/50"
            }`}>
              1
            </div>
            <span className={`font-label-sm text-label-sm ${step >= 1 ? "text-on-surface" : "text-on-surface-variant"}`}>Account</span>
          </div>
          <div className="relative z-10 flex flex-col items-center gap-sm bg-surface-container-lowest px-sm">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-label-sm text-label-sm border ${
              step >= 2 ? "bg-primary text-on-primary shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)]" : "bg-surface-variant text-on-surface-variant border-outline-variant/50"
            }`}>
              2
            </div>
            <span className={`font-label-sm text-label-sm ${step >= 2 ? "text-on-surface" : "text-on-surface-variant"}`}>Farm</span>
          </div>
        </div>

        {error && (
          <div className="mb-md rounded-lg bg-error-container p-3 font-body-sm font-medium text-on-error-container">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-lg">
          {step === 1 && (
            <div className="space-y-md">
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Full Name</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">person</span>
                  <input
                    className={inputClass}
                    placeholder="Jane Doe"
                    type="text"
                    value={form.fullName}
                    onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Email Address</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">mail</span>
                  <input
                    className={inputClass}
                    placeholder="jane@farm.com"
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Password</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">lock</span>
                  <input
                    className={inputClass}
                    placeholder="••••••••"
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Confirm Password</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">lock_reset</span>
                  <input
                    className={inputClass}
                    placeholder="••••••••"
                    type="password"
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-md">
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Farm Name</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">agriculture</span>
                  <input
                    className={inputClass}
                    placeholder="North Field"
                    type="text"
                    value={form.farmName}
                    onChange={(e) => setForm({ ...form, farmName: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Location (District)</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">pin_drop</span>
                  <select
                    className={`${inputClass} appearance-none`}
                    value={form.location}
                    onChange={(e) => setForm({ ...form, location: e.target.value })}
                  >
                    <option value="">Select a district</option>
                    {LOCATIONS.map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-start gap-sm mt-md">
            <input className="mt-1 w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/20" id="terms" type="checkbox" required />
            <label className="font-body-sm text-body-sm text-on-surface-variant" htmlFor="terms">
              I agree to the <span className="text-primary hover:underline font-medium cursor-pointer">Terms of Service</span> and <span className="text-primary hover:underline font-medium cursor-pointer">Privacy Policy</span>.
            </label>
          </div>

          <button
            type="submit"
            disabled={busy}
            className="w-full bg-primary-container text-white rounded-lg py-sm font-label-md text-label-md shadow-[inset_0_1px_1px_rgba(255,255,255,0.4)] transition-colors duration-200 mt-xl flex items-center justify-center gap-sm hover:bg-primary"
          >
            {busy ? "Creating Account..." : step === 1 ? "Next Step" : "Create Account & Add Farm"}
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </form>

        <div className="mt-2xl text-center border-t border-outline-variant/30 pt-lg">
          {step === 1 ? (
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Already have an account?{" "}
              <Link to="/login" className="text-primary hover:underline font-medium ml-xs">
                Sign In
              </Link>
            </p>
          ) : (
            <button
              onClick={() => { setStep(1); setError(""); }}
              className="inline-flex items-center gap-xs font-label-sm text-label-sm text-on-surface-variant hover:text-on-surface transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              Back to account details
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
