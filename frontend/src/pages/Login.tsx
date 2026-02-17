import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const Login: React.FC = () => {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const { login }   = useAuth();
  const navigate    = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch {
      setError('Correo o contraseña incorrectos. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={S.root}>
      <style>{CSS}</style>
      <div style={S.card} className="it-in">

        {/* Logo */}
        <div style={S.logoWrap}>
          <div style={S.logoIcon}><span style={{fontSize:28}}>💬</span></div>
          <h1 style={S.logoText}>
            <span style={{color:'#1e4d7b'}}>Inclu</span><span style={{color:'#2cb87a'}}>Talk</span>
          </h1>
        </div>
        <p style={S.subtitle}>Sistema de Atención Inclusiva</p>

        <form onSubmit={handleSubmit} style={S.form}>
          <div style={S.field}>
            <label style={S.label}>Correo electrónico</label>
            <input
              type="email" value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="usuario@institucion.pe"
              required style={S.input} autoFocus
            />
          </div>

          <div style={S.field}>
            <label style={S.label}>Contraseña</label>
            <input
              type="password" value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required style={S.input}
            />
          </div>

          {error && (
            <div style={S.errBox}>
              <span>⚠️</span><span>{error}</span>
            </div>
          )}

          <button type="submit" disabled={loading}
            style={{...S.submitBtn, opacity: loading ? 0.7 : 1}}>
            {loading ? '⏳ Verificando…' : 'Iniciar sesión'}
          </button>
        </form>

        <p style={S.footer}>IncluTalk · Diamond Impact</p>
      </div>
      <div style={S.version}>MVP v1.0</div>
    </div>
  );
};

const S: Record<string, React.CSSProperties> = {
  root: {
    minHeight: '100vh',
    background: 'linear-gradient(150deg,#f0f9f4 0%,#e8f4fb 50%,#f5f0ff 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontFamily: '"Inter",system-ui,sans-serif', padding: 20,
  },
  card: {
    background: '#fff', borderRadius: 24, padding: '48px 44px',
    width: '100%', maxWidth: 420,
    boxShadow: '0 8px 40px rgba(0,0,0,.10)',
    border: '1px solid rgba(0,0,0,.06)',
    display: 'flex', flexDirection: 'column', alignItems: 'center',
  },
  logoWrap: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 },
  logoIcon: {
    width: 52, height: 52, borderRadius: 14,
    background: 'linear-gradient(135deg,#e6f7f1,#e8f0f7)',
    border: '1.5px solid #a7f3d0',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  logoText: { fontSize: 32, fontWeight: 800, margin: 0, letterSpacing: -0.5 },
  subtitle: { fontSize: 15, color: '#6b7280', margin: '0 0 32px', textAlign: 'center' },
  form: { width: '100%', display: 'flex', flexDirection: 'column', gap: 18 },
  field: { display: 'flex', flexDirection: 'column', gap: 6 },
  label: { fontSize: 14, fontWeight: 600, color: '#374151' },
  input: {
    width: '100%', padding: '13px 16px', borderRadius: 12,
    border: '1.5px solid #d1d5db', fontSize: 15, fontFamily: 'inherit',
    color: '#111827', background: '#f9fafb', outline: 'none',
    boxSizing: 'border-box', transition: 'border-color .2s',
  },
  errBox: {
    background: '#fff0f0', border: '1px solid #fecaca',
    borderRadius: 10, padding: '12px 16px',
    color: '#dc2626', fontSize: 14, fontWeight: 500,
    display: 'flex', alignItems: 'center', gap: 8,
  },
  submitBtn: {
    width: '100%', padding: 15, borderRadius: 12, border: 'none',
    background: 'linear-gradient(135deg,#1e7a52,#2cb87a)',
    color: '#fff', fontSize: 17, fontWeight: 700,
    cursor: 'pointer', fontFamily: 'inherit',
    boxShadow: '0 4px 14px rgba(44,184,122,.35)',
    marginTop: 4,
  },
  footer: { fontSize: 12, color: '#9ca3af', margin: '24px 0 0', textAlign: 'center' },
  version: {
    position: 'fixed', bottom: 16, right: 16,
    background: 'rgba(255,255,255,.8)', border: '1px solid #e5e7eb',
    borderRadius: 8, padding: '4px 10px', fontSize: 11, color: '#9ca3af',
    fontFamily: '"Inter",sans-serif',
  },
};

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  @keyframes it-in { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
  .it-in { animation: it-in .4s ease both; }
  input:focus { border-color: #2cb87a !important; background: #fff !important; box-shadow: 0 0 0 3px rgba(44,184,122,.15); }
`;