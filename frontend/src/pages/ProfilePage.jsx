import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function ProfilePage() {
  const { user } = useAuth();
  const toast = useToast();
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    fullName: user?.full_name || "",
    email: user?.email || "",
    phone: "+1 (555) 924-1029",
    language: "en",
    role: "Senior Agronomist",
    organization: "Veridian Valley Orchards",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    // TODO: connect to backend
    await new Promise((r) => setTimeout(r, 1200));
    setSaving(false);
    toast.success("Profile updated successfully.");
  }

  function handleDiscard() {
    setForm({
      fullName: user?.full_name || "",
      email: user?.email || "",
      phone: "+1 (555) 924-1029",
      language: "en",
      role: "Senior Agronomist",
      organization: "Veridian Valley Orchards",
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
  }

  return (
    <div className="max-w-4xl mx-auto space-y-xl pb-2xl">
      <form onSubmit={handleSave}>
        {/* Personal Information */}
        <section className="bg-surface rounded-xl border border-outline-variant shadow-sm p-xl overflow-hidden mb-xl">
          <div className="flex flex-col md:flex-row gap-xl items-start">
            <div className="flex flex-col items-center gap-md w-full md:w-auto">
              <div className="relative group">
                <div className="w-32 h-32 rounded-full border-4 border-surface-container-highest overflow-hidden shadow-sm bg-surface-container-high flex items-center justify-center">
                  <span className="material-symbols-outlined text-6xl text-on-surface-variant/40">person</span>
                </div>
                <label className="absolute bottom-0 right-0 bg-primary text-on-primary w-10 h-10 rounded-full flex items-center justify-center shadow-lg hover:scale-105 transition-transform cursor-pointer">
                  <span className="material-symbols-outlined text-[20px]">edit</span>
                  <input type="file" accept="image/*" className="hidden" />
                </label>
              </div>
              <div className="text-center">
                <p className="text-label-md font-label-md text-on-surface">Profile Photo</p>
                <p className="text-label-sm text-on-surface-variant">SVG, PNG, JPG up to 10MB</p>
              </div>
            </div>

            <div className="flex-1 w-full space-y-lg">
              <h2 className="text-headline-sm font-headline-sm text-primary">Personal Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
                <div className="flex flex-col gap-xs">
                  <label className="text-label-md font-label-md text-on-surface-variant">Full Name</label>
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all"
                    type="text"
                    value={form.fullName}
                    onChange={(e) => update("fullName", e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-xs">
                  <label className="text-label-md font-label-md text-on-surface-variant">Email Address</label>
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all"
                    type="email"
                    value={form.email}
                    onChange={(e) => update("email", e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-xs">
                  <label className="text-label-md font-label-md text-on-surface-variant">Phone Number</label>
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all"
                    type="tel"
                    value={form.phone}
                    onChange={(e) => update("phone", e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-xs">
                  <label className="text-label-md font-label-md text-on-surface-variant">Language Preference</label>
                  <select
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none transition-all appearance-none cursor-pointer"
                    value={form.language}
                    onChange={(e) => update("language", e.target.value)}
                  >
                    <option value="en">English (US)</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="pt">Português</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Professional Details */}
        <section className="bg-surface rounded-xl border border-outline-variant shadow-sm p-xl mb-xl">
          <div className="flex items-center gap-md mb-lg">
            <span className="material-symbols-outlined text-primary">work</span>
            <h2 className="text-headline-sm font-headline-sm text-primary">Professional Details</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-label-md text-on-surface-variant">Professional Role</label>
              <div className="relative">
                <span className="absolute left-md top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-[18px]">psychology</span>
                <input
                  className="w-full pl-xl pr-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none"
                  type="text"
                  value={form.role}
                  onChange={(e) => update("role", e.target.value)}
                />
              </div>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-label-md text-on-surface-variant">Organization / Farm Name</label>
              <div className="relative">
                <span className="absolute left-md top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-[18px]">agriculture</span>
                <input
                  className="w-full pl-xl pr-md py-sm border border-outline-variant rounded-lg bg-surface-container-low text-body-md focus:ring-2 focus:ring-primary-container focus:border-primary outline-none"
                  type="text"
                  value={form.organization}
                  onChange={(e) => update("organization", e.target.value)}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Security & Access */}
        <section className="bg-surface rounded-xl border border-outline-variant shadow-sm p-xl mb-xl">
          <div className="flex items-center gap-md mb-lg">
            <span className="material-symbols-outlined text-primary">security</span>
            <h2 className="text-headline-sm font-headline-sm text-primary">Security & Access</h2>
          </div>
          <div className="space-y-xl">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-lg pt-md">
              <div>
                <p className="text-label-md font-bold text-on-surface">Change Password</p>
                <p className="text-body-sm text-on-surface-variant mt-xs">Update your account credentials to maintain security.</p>
              </div>
              <div className="md:col-span-2 space-y-md">
                <div className="flex flex-col gap-xs">
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low focus:ring-2 focus:ring-primary-container outline-none"
                    placeholder="Current Password"
                    type="password"
                    value={form.currentPassword}
                    onChange={(e) => update("currentPassword", e.target.value)}
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-md">
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low focus:ring-2 focus:ring-primary-container outline-none"
                    placeholder="New Password"
                    type="password"
                    value={form.newPassword}
                    onChange={(e) => update("newPassword", e.target.value)}
                  />
                  <input
                    className="px-md py-sm border border-outline-variant rounded-lg bg-surface-container-low focus:ring-2 focus:ring-primary-container outline-none"
                    placeholder="Confirm New Password"
                    type="password"
                    value={form.confirmPassword}
                    onChange={(e) => update("confirmPassword", e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Actions */}
        <div className="flex items-center justify-end gap-md pt-lg border-t border-outline-variant">
          <button
            type="button"
            onClick={handleDiscard}
            className="px-xl py-md rounded-lg bg-surface text-on-surface border border-outline-variant hover:bg-surface-container-high transition-colors text-label-md font-label-md"
          >
            Discard Changes
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-xl py-md rounded-lg bg-primary text-on-primary hover:bg-primary/90 shadow-lg active:scale-[0.98] transition-all text-label-md font-label-md flex items-center gap-sm disabled:opacity-60"
          >
            {saving ? (
              <>
                <svg className="animate-spin h-5 w-5 text-on-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">save</span>
                Save Profile
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
