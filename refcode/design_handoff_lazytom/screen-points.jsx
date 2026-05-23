// LazyTom — Points screen (redesigned)

function ScreenPoints() {
  const history = [
    { task: 'Math Homework',        when: 'Today · 14:32', mins: 25, pts: 3, diff: 'Hard', diffColor: T.amber },
    { task: 'English Reading',      when: 'Today · 13:55', mins: 20, pts: 2, diff: 'Easy', diffColor: T.sky },
    { task: 'Piano Practice',       when: 'Today · 11:20', mins: 30, pts: 3, diff: 'Normal', diffColor: T.mossSoft },
    { task: 'Chinese Essay Draft',  when: 'Yesterday · 19:40', mins: 45, pts: 5, diff: 'Very Hard', diffColor: T.rose },
    { task: 'Science Lab Report',   when: 'Yesterday · 16:10', mins: 30, pts: 3, diff: 'Hard', diffColor: T.amber },
  ];
  const week = [3, 5, 2, 7, 4, 6, 4]; // pts per day, Mon..Sun
  const maxBar = Math.max(...week);

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      background: T.bg, padding: '20px 24px 0', overflow: 'hidden',
    }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div style={{ fontFamily: T.serif, fontSize: 30, color: T.ink, letterSpacing: -0.5 }}>Your Garden</div>
        <div style={{ fontSize: 10.5, color: T.inkMute, letterSpacing: 1, textTransform: 'uppercase', fontWeight: 500 }}>May</div>
      </div>

      {/* Hero card — big number */}
      <div style={{
        marginTop: 14,
        background: 'linear-gradient(160deg, #2F5A3A 0%, #1F3F28 100%)',
        borderRadius: 18, padding: '18px 20px',
        position: 'relative', overflow: 'hidden',
        boxShadow: '0 1px 0 rgba(255,255,255,0.1) inset, 0 12px 32px -16px rgba(31,42,33,0.4)',
      }}>
        {/* subtle pattern */}
        <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, opacity: 0.08 }}>
          <defs>
            <pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" fill="#F2EBD3" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)" />
        </svg>
        <div style={{ position: 'relative' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontSize: 11, color: 'rgba(242,235,211,0.7)', letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500 }}>
              Total points
            </div>
            <div style={{
              fontSize: 10, color: T.leaf, letterSpacing: 0.5, fontWeight: 500,
              background: 'rgba(168,196,154,0.18)', padding: '3px 8px', borderRadius: 999,
            }}>+4 today</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 6 }}>
            <div style={{ fontFamily: T.serif, fontSize: 64, lineHeight: 1, color: '#F7F2E4', letterSpacing: -2, fontVariantNumeric: 'tabular-nums' }}>
              127
            </div>
            <div style={{ fontFamily: T.serif, fontSize: 18, color: 'rgba(242,235,211,0.55)' }}>pts</div>
          </div>

          {/* week bars */}
          <div style={{ marginTop: 14, display: 'flex', alignItems: 'flex-end', gap: 8, height: 44 }}>
            {week.map((v, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 5 }}>
                <div style={{
                  width: '100%', height: `${(v / maxBar) * 32}px`, minHeight: 4,
                  background: i === 6 ? T.clay : 'rgba(242,235,211,0.55)',
                  borderRadius: 3,
                }} />
                <div style={{ fontSize: 9, color: 'rgba(242,235,211,0.55)', letterSpacing: 0.5 }}>
                  {['M','T','W','T','F','S','S'][i]}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* History section */}
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: 18 }}>
        <div style={{ fontSize: 12, color: T.inkSoft, fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase' }}>
          Recent sessions
        </div>
        <div style={{ fontSize: 11, color: T.inkMute, fontWeight: 500 }}>5 of 47</div>
      </div>

      <div style={{ marginTop: 10, flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
        {history.map((h, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '12px 4px',
            borderBottom: i < history.length - 1 ? `1px solid ${T.line}` : 'none',
          }}>
            <div style={{
              width: 3, height: 28, borderRadius: 2,
              background: h.diffColor,
            }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: T.ink, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {h.task}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 2 }}>
                <div style={{ fontSize: 10.5, color: T.inkMute, letterSpacing: 0.3 }}>{h.when}</div>
                <div style={{ width: 2, height: 2, borderRadius: 1, background: T.inkMute, opacity: 0.4 }} />
                <div style={{ fontSize: 10.5, color: T.inkMute, fontWeight: 500 }}>{h.mins}m · {h.diff}</div>
              </div>
            </div>
            <div style={{
              fontFamily: T.serif, fontSize: 22, color: T.moss,
              letterSpacing: -0.5, fontVariantNumeric: 'tabular-nums',
            }}>
              +{h.pts}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

window.ScreenPoints = ScreenPoints;
