// LazyTom — Timer screen (redesigned)

function ScreenTimer() {
  const total = 15 * 60;     // 15 min
  const elapsed = 0;          // ready state
  const progress = elapsed / total;
  const R = 118;              // ring radius
  const C = 2 * Math.PI * R;
  const dash = `${C * progress} ${C}`;

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      background: T.bg, padding: '18px 24px 0',
    }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{
            fontFamily: T.serif, fontSize: 30, lineHeight: 1, color: T.ink, letterSpacing: -0.5,
          }}>LazyTom</div>
          <div style={{
            fontSize: 11, color: T.inkMute, marginTop: 4, letterSpacing: 1.2,
            textTransform: 'uppercase', fontWeight: 500,
          }}>Tuesday, May 23</div>
        </div>
        {/* Streak chip */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6,
          background: T.paper, padding: '6px 10px 6px 8px',
          borderRadius: 999, border: `1px solid ${T.line}`,
          boxShadow: T.card,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M12 3c1 4 5 5 5 10a5 5 0 0 1-10 0c0-3 2-4 2-7 1 1 2 3 3 4 0-3 0-5 0-7z"
              fill={T.clay} stroke={T.clay} strokeWidth="1" strokeLinejoin="round" />
          </svg>
          <span style={{ fontSize: 12, fontWeight: 600, color: T.ink, fontVariantNumeric: 'tabular-nums' }}>4</span>
          <span style={{ fontSize: 10, color: T.inkSoft, fontWeight: 500, letterSpacing: 0.5 }}>DAY STREAK</span>
        </div>
      </div>

      {/* Session pills */}
      <div style={{ display: 'flex', gap: 6, marginTop: 18, justifyContent: 'center' }}>
        {[1,2,3,4,5].map(i => (
          <div key={i} style={{
            width: 22, height: 6, borderRadius: 3,
            background: i <= 2 ? T.moss : i === 3 ? T.leaf : T.line,
          }} />
        ))}
      </div>
      <div style={{
        marginTop: 6, fontSize: 10.5, color: T.inkMute, textAlign: 'center',
        letterSpacing: 1, textTransform: 'uppercase', fontWeight: 500,
      }}>Session 3 of 5 · Focus</div>

      {/* Ring */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', marginTop: 4,
      }}>
        {/* +/- controls */}
        <button style={ghostBtn(T)}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 12h14" /></svg>
        </button>

        <div style={{ position: 'relative', width: 260, height: 260, margin: '0 8px' }}>
          {/* tick marks */}
          <svg width="260" height="260" style={{ position: 'absolute', inset: 0 }}>
            {Array.from({ length: 60 }).map((_, i) => {
              const a = (i / 60) * Math.PI * 2 - Math.PI / 2;
              const r1 = 128, r2 = i % 5 === 0 ? 120 : 124;
              const x1 = 130 + Math.cos(a) * r1, y1 = 130 + Math.sin(a) * r1;
              const x2 = 130 + Math.cos(a) * r2, y2 = 130 + Math.sin(a) * r2;
              return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke={i % 5 === 0 ? T.inkSoft : T.inkMute}
                strokeOpacity={i % 5 === 0 ? 0.45 : 0.18}
                strokeWidth={i % 5 === 0 ? 1.2 : 0.8} strokeLinecap="round" />;
            })}
          </svg>
          {/* progress ring */}
          <svg width="260" height="260" style={{ position: 'absolute', inset: 0, transform: 'rotate(-90deg)' }}>
            <defs>
              <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#3F7A4B" />
                <stop offset="100%" stopColor="#2F5A3A" />
              </linearGradient>
            </defs>
            <circle cx="130" cy="130" r={R} fill="none" stroke="rgba(31,42,33,0.08)" strokeWidth="2" />
            <circle cx="130" cy="130" r={R} fill="none" stroke="url(#ring)" strokeWidth="3"
              strokeDasharray={dash} strokeLinecap="round" />
          </svg>
          {/* center */}
          <div style={{
            position: 'absolute', inset: 24, borderRadius: '50%',
            background: T.paper,
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.8), 0 8px 24px -12px rgba(31,42,33,0.18)',
          }}>
            <div style={{
              fontSize: 10, letterSpacing: 1.4, color: T.inkMute,
              textTransform: 'uppercase', fontWeight: 500,
            }}>Focus on</div>
            <div style={{
              fontSize: 12.5, color: T.ink, marginTop: 3, fontWeight: 500,
              maxWidth: 160, textAlign: 'center', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}>Math Homework</div>
            <div style={{
              fontFamily: T.serif, fontSize: 68, lineHeight: 1,
              color: T.ink, letterSpacing: -2, marginTop: 8,
              fontVariantNumeric: 'tabular-nums',
            }}>15:00</div>
            <div style={{
              marginTop: 6, fontSize: 10.5, color: T.inkMute,
              letterSpacing: 1, textTransform: 'uppercase', fontWeight: 500,
            }}>ends at 3:42 PM</div>
          </div>
        </div>

        <button style={ghostBtn(T)}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 5v14M5 12h14" /></svg>
        </button>
      </div>

      {/* Big start button */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, paddingBottom: 14 }}>
        <button style={{
          display: 'flex', alignItems: 'center', gap: 12,
          background: T.moss, color: '#F7F2E4',
          padding: '14px 32px 14px 26px',
          borderRadius: 999, border: 'none',
          fontFamily: T.sans, fontSize: 15, fontWeight: 600, letterSpacing: 0.3,
          boxShadow: T.press, cursor: 'pointer',
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 4l14 8-14 8V4z" />
          </svg>
          Begin Focus
        </button>
        <div style={{
          fontSize: 11, color: T.inkSoft, letterSpacing: 0.4,
        }}>
          <span style={{ color: T.inkMute }}>Notifications muted ·</span> Tap to start
        </div>
      </div>
    </div>
  );
}

function ghostBtn(T) {
  return {
    width: 36, height: 36, borderRadius: 999,
    background: 'transparent', border: `1px solid ${T.lineStr}`,
    color: T.inkSoft, display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', flexShrink: 0,
  };
}

window.ScreenTimer = ScreenTimer;
