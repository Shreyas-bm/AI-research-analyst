import React, { useState } from 'react';
import { Lock, Mail, User as UserIcon, Eye, EyeOff, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const AuthScreen: React.FC = () => {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (mode === 'login') {
        await login({ email, password });
      } else {
        await register({ email, password, full_name: fullName });
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#0D1017] text-[#E8E9ED] flex flex-col justify-between p-6 sm:p-12 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#2F8F8B]/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Top Header */}
      <div className="flex items-center justify-between max-w-6xl mx-auto w-full z-10">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#2F8F8B] to-[#181D2B] border border-[#2F8F8B]/40 flex items-center justify-center text-white font-mono font-bold text-sm shadow-md">
            DL
          </div>
          <div>
            <div className="font-serif font-bold text-lg text-[#E8E9ED] tracking-tight">
              DecisionLens
            </div>
            <div className="font-mono text-[10px] text-[#2F8F8B] tracking-wider uppercase font-semibold">
              Evidence-First Decision Engine
            </div>
          </div>
        </div>

        <div className="inline-flex items-center space-x-2 font-mono text-xs text-[#8E96A5] bg-[#181D2B] px-3 py-1.5 rounded-full border border-[#262D3D]">
          <span className="w-2 h-2 rounded-full bg-[#4C8B5B]"></span>
          <span>Zero-Hallucination Claim Verification</span>
        </div>
      </div>

      {/* Center Auth Card */}
      <div className="max-w-md w-full mx-auto my-auto py-8 z-10">
        <div className="bg-[#10131C] border border-[#262D3D] rounded-2xl shadow-2xl p-8 text-[#E8E9ED]">
          
          {/* Card Header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#2F8F8B]/15 text-[#2F8F8B] border border-[#2F8F8B]/30 mb-3">
              <Lock className="w-6 h-6" />
            </div>
            <h1 className="font-serif text-2xl font-bold text-[#E8E9ED]">
              {mode === 'login' ? 'Sign In to DecisionLens' : 'Create DecisionLens Account'}
            </h1>
            <p className="text-xs text-[#8E96A5] mt-1.5 font-sans leading-relaxed">
              {mode === 'login' 
                ? 'Sign in to access your verified multi-agent research runs and benchmark explorer.' 
                : 'Register your account with secure PBKDF2-HMAC-SHA256 password hashing.'}
            </p>
          </div>

          {/* Mode Tab Switcher */}
          <div className="flex bg-[#181D2B] p-1 rounded-lg border border-[#262D3D] mb-6">
            <button
              type="button"
              onClick={() => { setMode('login'); setError(null); }}
              className={`flex-1 py-2 text-xs font-mono font-bold rounded-md transition-all cursor-pointer ${
                mode === 'login' 
                  ? 'bg-[#262D3D] text-[#E8E9ED] shadow-xs' 
                  : 'text-[#8E96A5] hover:text-[#E8E9ED]'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setMode('register'); setError(null); }}
              className={`flex-1 py-2 text-xs font-mono font-bold rounded-md transition-all cursor-pointer ${
                mode === 'register' 
                  ? 'bg-[#262D3D] text-[#E8E9ED] shadow-xs' 
                  : 'text-[#8E96A5] hover:text-[#E8E9ED]'
              }`}
            >
              Register
            </button>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 p-3 bg-[#C1553B]/20 border border-[#C1553B]/50 rounded-lg text-[#F28B82] text-xs font-mono flex items-center justify-between">
              <span>{error}</span>
              <button onClick={() => setError(null)} className="ml-2 font-bold cursor-pointer">✕</button>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-xs font-mono uppercase text-[#8E96A5] mb-1.5 font-semibold">
                  Full Name
                </label>
                <div className="relative">
                  <UserIcon className="absolute left-3.5 top-3 w-4 h-4 text-[#8E96A5]" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Alex Rivera"
                    className="w-full pl-10 pr-4 py-2.5 bg-[#181D2B] border border-[#262D3D] focus:border-[#2F8F8B] rounded-lg text-xs text-[#E8E9ED] placeholder:text-[#5D646F] outline-none transition-all"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono uppercase text-[#8E96A5] mb-1.5 font-semibold">
                Email Address <span className="text-[#C1553B]">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-4 h-4 text-[#8E96A5]" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="architect@domain.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#181D2B] border border-[#262D3D] focus:border-[#2F8F8B] rounded-lg text-xs text-[#E8E9ED] placeholder:text-[#5D646F] outline-none transition-all font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-[#8E96A5] mb-1.5 font-semibold">
                Password <span className="text-[#C1553B]">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-4 h-4 text-[#8E96A5]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={mode === 'register' ? 'Minimum 6 characters' : 'Enter your password'}
                  className="w-full pl-10 pr-10 py-2.5 bg-[#181D2B] border border-[#262D3D] focus:border-[#2F8F8B] rounded-lg text-xs text-[#E8E9ED] placeholder:text-[#5D646F] outline-none transition-all font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3 text-[#8E96A5] hover:text-[#E8E9ED] cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 py-3.5 bg-[#2F8F8B] hover:bg-[#277874] text-white font-mono text-xs font-bold uppercase tracking-wider rounded-lg transition-all shadow-md hover:shadow-lg disabled:opacity-50 flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>
                {isSubmitting 
                  ? (mode === 'login' ? 'Authenticating...' : 'Creating Account...') 
                  : (mode === 'login' ? 'Sign In' : 'Create Account')}
              </span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Security Badge */}
          <div className="mt-6 pt-4 border-t border-[#262D3D] flex items-center justify-center space-x-2 text-[11px] font-mono text-[#8E96A5]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#4C8B5B]" />
            <span>PBKDF2-HMAC-SHA256 Password Hashing & JWT</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-6xl mx-auto w-full text-center text-xs font-mono text-[#5D646F] z-10">
        DecisionLens Evidence Engine &copy; 2026 &bull; Cryptographically Verified Local Architecture
      </div>
    </div>
  );
};
