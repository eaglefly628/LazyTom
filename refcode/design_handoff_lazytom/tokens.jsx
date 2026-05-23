// LazyTom Design Tokens — sophisticated, warm, modern

const T = {
  // Palette — warm cream + deep forest + clay accent
  bg:        '#EFE9D9',  // warm linen
  paper:     '#F7F2E4',  // card / surface
  ink:       '#1F2A21',  // near-black green
  inkSoft:   '#5C6655',
  inkMute:   '#9AA193',
  line:      'rgba(31,42,33,0.08)',
  lineStr:   'rgba(31,42,33,0.14)',

  // Brand
  moss:      '#2F5A3A',  // deep moss — primary
  mossSoft:  '#5C8A5C',
  leaf:      '#A8C49A',  // muted sage
  cream:     '#F2EBD3',  // accent cream pill

  // Accents
  clay:      '#C97A57',  // terracotta — "now do this"
  amber:     '#D9A24E',  // medium difficulty
  rose:      '#B85A5A',  // very hard
  sky:       '#7AA2C2',  // easy
  shell:     '#E8DCC0',  // very easy

  // Typography
  serif:  '"Instrument Serif", "Cormorant Garamond", Georgia, serif',
  sans:   '"Geist", "Inter", -apple-system, BlinkMacSystemFont, sans-serif',
  mono:   '"Geist Mono", "JetBrains Mono", ui-monospace, monospace',

  // Shadows
  card:   '0 1px 0 rgba(255,255,255,0.6) inset, 0 1px 2px rgba(31,42,33,0.04), 0 8px 24px -8px rgba(31,42,33,0.08)',
  cardHi: '0 1px 0 rgba(255,255,255,0.7) inset, 0 4px 12px rgba(31,42,33,0.08), 0 24px 48px -16px rgba(31,42,33,0.12)',
  press:  '0 12px 32px -8px rgba(47,90,58,0.45)',
};

// Phone-like window frame (mimics macOS small window, matches original screenshots)
function LTFrame({ children, label, width = 400, height = 720 }) {
  return (
    <div style={{
      width, height, borderRadius: 22, overflow: 'hidden',
      background: T.bg,
      boxShadow: '0 0 0 1px rgba(31,42,33,0.10), 0 30px 60px -20px rgba(31,42,33,0.35)',
      display: 'flex', flexDirection: 'column',
      fontFamily: T.sans, color: T.ink,
      position: 'relative',
    }}>
      {/* Title bar */}
      <div style={{
        height: 36, flexShrink: 0,
        background: '#1F1F1F',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative',
      }}>
        <div style={{
          position: 'absolute', left: 12, top: 0, bottom: 0,
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <div style={{ width: 12, height: 12, borderRadius: 6, background: '#FF5F57' }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, background: '#FEBC2E' }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, background: '#28C840' }} />
        </div>
        <div style={{
          fontFamily: T.sans, fontSize: 13, fontWeight: 500,
          color: '#E6E1D2', letterSpacing: 0.2,
        }}>LazyTom</div>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {children}
      </div>
    </div>
  );
}

// Bottom tab bar — refined, glass, no chunky pill backgrounds
function LTTabBar({ active = 'timer' }) {
  const tabs = [
    { id: 'timer',    label: 'Timer',    icon: 'timer' },
    { id: 'points',   label: 'Points',   icon: 'star' },
    { id: 'tasks',    label: 'Tasks',    icon: 'tasks' },
    { id: 'settings', label: 'Settings', icon: 'gear' },
  ];
  const Icon = ({ name, on }) => {
    const s = { width: 22, height: 22, fill: 'none', stroke: 'currentColor', strokeWidth: 1.6, strokeLinecap: 'round', strokeLinejoin: 'round' };
    if (name === 'timer') return (
      <svg viewBox="0 0 24 24" style={s}><circle cx="12" cy="13" r="8" /><path d="M12 13V8" /><path d="M9 3h6" /><path d="M19 5l1.5-1.5" /></svg>
    );
    if (name === 'star') return (
      <svg viewBox="0 0 24 24" style={s}><path d="M12 3l2.5 5.5L20 9.5l-4 4 1 6L12 16.5 7 19.5l1-6-4-4 5.5-1z" /></svg>
    );
    if (name === 'tasks') return (
      <svg viewBox="0 0 24 24" style={s}><path d="M4 7l2 2 3-3" /><path d="M4 14l2 2 3-3" /><path d="M12 8h8" /><path d="M12 15h8" /></svg>
    );
    return (
      <svg viewBox="0 0 24 24" style={s}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" /></svg>
    );
  };
  return (
    <div style={{
      flexShrink: 0, padding: '10px 12px 14px',
      borderTop: `1px solid ${T.line}`,
      background: T.bg,
      display: 'flex', justifyContent: 'space-around',
    }}>
      {tabs.map(t => {
        const on = t.id === active;
        return (
          <div key={t.id} style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            color: on ? T.moss : T.inkMute,
            fontSize: 10.5, fontWeight: on ? 600 : 500, letterSpacing: 0.3,
            position: 'relative', padding: '4px 8px',
          }}>
            {on && <div style={{
              position: 'absolute', top: -10, left: '50%', transform: 'translateX(-50%)',
              width: 24, height: 3, borderRadius: 2, background: T.moss,
            }} />}
            <Icon name={t.icon} on={on} />
            <span style={{ textTransform: 'uppercase' }}>{t.label}</span>
          </div>
        );
      })}
    </div>
  );
}

Object.assign(window, { T, LTFrame, LTTabBar });
