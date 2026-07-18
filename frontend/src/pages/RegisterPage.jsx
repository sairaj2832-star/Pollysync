import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../lib/api";

const LOCATIONS = [
  "Amravati", "Andhra Pradesh", "Assam", "Aurangabad",
  "Bihar", "Chhattisgarh", "Gujarat", "Haryana",
  "Jalgaon", "Jharkhand", "Karnataka", "Kerala",
  "Kolhapur", "Latur", "Madhya Pradesh", "Maharashtra",
  "Nagpur", "Nashik", "Odisha", "Pune", "Punjab",
  "Rajasthan", "Satara", "Solapur", "Tamil Nadu",
  "Telangana", "Uttar Pradesh", "Uttarakhand", "West Bengal",
];

export default function RegisterPage() {
  const { user, loading: authLoading, register, isFirebaseConfigured } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "", password: "", fullName: "",
    confirmPassword: "", farmName: "", location: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [step, setStep] = useState(1);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [busy, setBusy] = useState(false);

  if (authLoading) {
    return (
      <div className="bg-background min-h-screen flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (user) return <Navigate to="/dashboard" replace />;

  function validateStep1() {
    const errors = {};
    if (!form.fullName.trim()) errors.fullName = "Full name is required";
    if (!form.email.trim()) errors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(form.email)) errors.email = "Enter a valid email address";
    if (!form.password) errors.password = "Password is required";
    else if (form.password.length < 10) errors.password = "Must be at least 10 characters";
    if (!form.confirmPassword) errors.confirmPassword = "Please confirm your password";
    else if (form.password !== form.confirmPassword) errors.confirmPassword = "Passwords do not match";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (step === 1) {
      if (!validateStep1()) return;
      setStep(2);
      return;
    }

    setBusy(true);
    try {
      await register(form.email, form.password, form.fullName);
      navigate("/dashboard");
    } catch (err) {
      if (err?.code === "auth/email-already-in-use") {
        setError("This email is already registered. Please sign in instead.");
      } else if (err?.code === "auth/weak-password") {
        setError("Choose a stronger password with at least 6 characters.");
      } else if (err?.code === "auth/invalid-email") {
        setError("Please enter a valid email address.");
      } else {
        setError(getApiErrorMessage(err, "Registration failed"));
      }
    } finally {
      setBusy(false);
    }
  }

  const inputClass = "w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-2xl pr-md py-sm font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-on-surface-variant/50";
  const inputErrorClass = "border-error focus:border-error focus:ring-error/20";

  return (
    <div className="bg-background min-h-screen flex items-center justify-center p-lg relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary-container/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary-container/10 rounded-full blur-3xl pointer-events-none" />

      <main className="w-full max-w-[480px] bg-surface-container-lowest rounded-xl border border-outline-variant/30 shadow-[0_1px_3px_rgba(0,0,0,0.05)] p-xl relative z-10">
        <div className="text-center mb-xl">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary-container/20 text-primary mb-md">
            <span className="material-symbols-outlined text-[28px] filled">agriculture</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-xs">
            {step === 1 ? "Create your account" : "Farm details (optional)"}
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant">
            {step === 1
              ? "Set up your PolliSync account to get started."
              : "Tell us about your farm — you can skip and do this later."}
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

        {!isFirebaseConfigured && (
          <div className="mb-md rounded-lg bg-secondary-container/30 p-3 font-body-sm text-on-surface-variant">
            Firebase is not configured. Set <code className="font-mono text-xs bg-surface-container-high px-1 rounded">VITE_FIREBASE_*</code> keys in <code className="font-mono text-xs bg-surface-container-high px-1 rounded">frontend/.env</code>.
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
                    className={`${inputClass} ${fieldErrors.fullName ? inputErrorClass : ""}`}
                    placeholder="Jane Doe"
                    type="text"
                    value={form.fullName}
                    onChange={(e) => { setForm({ ...form, fullName: e.target.value }); setFieldErrors({ ...fieldErrors, fullName: "" }); }}
                  />
                </div>
                {fieldErrors.fullName && <span className="font-body-sm text-body-sm text-error mt-xs">{fieldErrors.fullName}</span>}
              </div>

              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Email Address</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">mail</span>
                  <input
                    className={`${inputClass} ${fieldErrors.email ? inputErrorClass : ""}`}
                    placeholder="jane@farm.com"
                    type="email"
                    value={form.email}
                    onChange={(e) => { setForm({ ...form, email: e.target.value }); setFieldErrors({ ...fieldErrors, email: "" }); }}
                  />
                </div>
                {fieldErrors.email && <span className="font-body-sm text-body-sm text-error mt-xs">{fieldErrors.email}</span>}
              </div>

              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Password</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">lock</span>
                  <input
                    className={`${inputClass} ${fieldErrors.password ? inputErrorClass : ""}`}
                    placeholder="••••••••"
                    type={showPassword ? "text" : "password"}
                    value={form.password}
                    onChange={(e) => { setForm({ ...form, password: e.target.value }); setFieldErrors({ ...fieldErrors, password: "" }); }}
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
                {fieldErrors.password && <span className="font-body-sm text-body-sm text-error mt-xs">{fieldErrors.password}</span>}
              </div>

              <div className="flex flex-col gap-xs">
                <label className="font-label-md text-label-md text-on-surface">Confirm Password</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">lock_reset</span>
                  <input
                    className={`${inputClass} ${fieldErrors.confirmPassword ? inputErrorClass : ""}`}
                    placeholder="••••••••"
                    type={showConfirm ? "text" : "password"}
                    value={form.confirmPassword}
                    onChange={(e) => { setForm({ ...form, confirmPassword: e.target.value }); setFieldErrors({ ...fieldErrors, confirmPassword: "" }); }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(!showConfirm)}
                    className="absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-on-surface transition-colors"
                    tabIndex={-1}
                  >
                    <span className="material-symbols-outlined text-[20px]">{showConfirm ? "visibility_off" : "visibility"}</span>
                  </button>
                </div>
                {fieldErrors.confirmPassword && <span className="font-body-sm text-body-sm text-error mt-xs">{fieldErrors.confirmPassword}</span>}
              </div>

              <div className="flex items-start gap-sm mt-md">
                <input className="mt-1 w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/20" id="terms" type="checkbox" required />
                <label className="font-body-sm text-body-sm text-on-surface-variant" htmlFor="terms">
                  I agree to the <span className="text-primary hover:underline font-medium cursor-pointer">Terms of Service</span> and <span className="text-primary hover:underline font-medium cursor-pointer">Privacy Policy</span>.
                </label>
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
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Optional. You can add farm details after sign-up.
                </p>
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
                <p className="font-body-sm text-body-sm text-on-surface-variant">
                  Optional. Farm onboarding continues inside the app.
                </p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full bg-primary hover:brightness-90 text-on-primary font-label-md text-label-md py-[12px] rounded-lg shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_1px_2px_rgba(0,0,0,0.1)] transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-sm"
          >
            {busy ? (
              <span className="flex items-center gap-sm">
                <span className="w-4 h-4 border-2 border-on-primary/30 border-t-on-primary rounded-full animate-spin" />
                Creating Account...
              </span>
            ) : (
              <>
                {step === 1 ? "Next Step" : "Create Account"}
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </>
            )}
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
