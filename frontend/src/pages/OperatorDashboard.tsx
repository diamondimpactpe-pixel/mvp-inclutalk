import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const OperatorDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div style={S.root}>
      <style>{CSS}</style>

      {/* Header */}
      <header style={S.header}>
        <div style={S.logo}>
          <span style={{color:'#1e4d7b'}}>Inclu</span>
          <span style={{color:'#2cb87a'}}>Talk</span>
        </div>
        <div style={S.headerRight}>
          <div style={S.userBadge}>
            <div style={S.userAvatar}>
              {user?.full_name?.charAt(0).toUpperCase() ?? 'O'}
            </div>
            <span style={S.userName}>{user?.full_name}</span>
          </div>
          <button style={S.logoutBtn} onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {/* Main */}
      <main style={S.main}>
        <div style={S.card} className="it-in">

          {/* Ícono central */}
          <div style={S.heroIcon}>
            <span style={{fontSize: 56}}>🏥</span>
          </div>

          <h2 style={S.cardTitle}>Panel del Operador</h2>
          <p style={S.cardSub}>
            Inicia una nueva sesión de atención inclusiva para comunicarte<br/>
            con personas con discapacidad auditiva o del habla.
          </p>

          {/* Botón principal */}
          <button style={S.startBtn} onClick={() => navigate('/attention')}>
            🚀 Iniciar Atención
          </button>

          {/* Info chips */}
          <div style={S.chips}>
            <div style={S.chip('#e6f7f1','#166534')}>🎤 Voz → Texto</div>
            <div style={S.chip('#e8f0f7','#1e40af')}>🤟 Señas LSP</div>
            <div style={S.chip('#f3eeff','#6d28d9')}>🔊 Texto → Voz</div>
          </div>
        </div>

        {/* Card info pequeña */}
        <div style={S.infoCard} className="it-in" >
          <p style={{margin:0, fontSize:13, color:'#9ca3af', textAlign:'center'}}>
            <strong style={{color:'#6b7280'}}>¿Cómo funciona?</strong>
            &nbsp;·&nbsp; El operador habla → se muestra en texto para el usuario sordo.
            El usuario responde con señas o texto → el sistema lo lee en voz alta al operador.
          </p>
        </div>
      </main>

      {/* Footer */}
      <footer style={S.footer}>
        <span style={{color:'#9ca3af', fontSize:12}}>
          IncluTalk · Diamond Impact · MVP v1.0
        </span>
      </footer>
    </div>
  );
};

const chip = (bg: string, color: string): React.CSSProperties => ({
  background: bg, color, border: `1px solid ${color}33`,
  borderRadius: 20, padding: '6px 16px', fontSize: 13, fontWeight: 600,
});

const S: Record<string, any> = {
  root: {
    minHeight: '100vh',
    background: 'linear-gradient(150deg,#f0f9f4 0%,#e8f4fb 50%,#f5f0ff 100%)',
    fontFamily: '"Inter",system-ui,sans-serif',
    color: '#1a2e3b',
    display: 'flex', flexDirection: 'column',
  },
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '14px 36px',
    background: '#fff',
    boxShadow: '0 1px 12px rgba(0,0,0,.08)',
    position: 'sticky', top: 0, zIndex: 100,
  },
  logo: { fontWeight: 800, fontSize: 26, letterSpacing: -0.5 },
  headerRight: { display: 'flex', alignItems: 'center', gap: 16 },
  userBadge: {
    display: 'flex', alignItems: 'center', gap: 10,
    background: '#f9fafb', border: '1px solid #e5e7eb',
    borderRadius: 12, padding: '7px 14px',
  },
  userAvatar: {
    width: 30, height: 30, borderRadius: '50%',
    background: 'linear-gradient(135deg,#1e7a52,#2cb87a)',
    color: '#fff', fontWeight: 700, fontSize: 14,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  userName: { fontSize: 14, fontWeight: 600, color: '#374151' },
  logoutBtn: {
    background: '#fff0f0', border: '1px solid #fecaca',
    borderRadius: 10, padding: '8px 18px', color: '#dc2626',
    cursor: 'pointer', fontSize: 14, fontWeight: 600, fontFamily: 'inherit',
  },
  main: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    padding: '40px 20px', gap: 20,
  },
  card: {
    background: '#fff', borderRadius: 24, padding: '52px 48px',
    width: '100%', maxWidth: 560, textAlign: 'center',
    boxShadow: '0 8px 40px rgba(0,0,0,.10)',
    border: '1px solid rgba(0,0,0,.06)',
    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20,
  },
  heroIcon: {
    width: 100, height: 100, borderRadius: 24,
    background: 'linear-gradient(135deg,#e6f7f1,#e8f0f7)',
    border: '2px solid #a7f3d0',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  cardTitle: {
    fontSize: 32, fontWeight: 800, color: '#111827',
    margin: 0, letterSpacing: -0.5,
  },
  cardSub: {
    fontSize: 16, color: '#6b7280', margin: 0, lineHeight: 1.6,
  },
  startBtn: {
    padding: '18px 56px', borderRadius: 16, border: 'none',
    background: 'linear-gradient(135deg,#1e7a52,#2cb87a)',
    color: '#fff', fontSize: 20, fontWeight: 700,
    cursor: 'pointer', fontFamily: 'inherit',
    boxShadow: '0 4px 20px rgba(44,184,122,.4)',
    transition: 'transform .15s, box-shadow .15s',
    marginTop: 4,
  },
  chips: { display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' },
  chip,
  infoCard: {
    background: '#fff', borderRadius: 16, padding: '16px 28px',
    width: '100%', maxWidth: 560,
    border: '1px solid rgba(0,0,0,.06)',
    boxShadow: '0 2px 12px rgba(0,0,0,.05)',
  },
  footer: {
    padding: '16px 36px', background: '#fff',
    borderTop: '1px solid #f3f4f6',
    display: 'flex', justifyContent: 'center',
  },
};

const CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  @keyframes it-in { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
  .it-in { animation: it-in .4s ease both; }
  button:hover { filter: brightness(.95); }
`;