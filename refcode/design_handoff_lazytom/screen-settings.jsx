// LazyTom — Settings screen (redesigned)

function ScreenSettings() {
  const [theme, setTheme] = React.useState('meadow');
  const [focus, setFocus] = React.useState(25);
  const [brk, setBrk] = React.useState(5);
  const [sound, setSound] = React.useState('chime');
  const [doNotDisturb, setDND] = React.useState(true);

  const themes = [
    { id: 'lakeside', label: 'Lakeside', sub: 'Cool blues', colors: ['#E3EEF4', '#7AA2C2', '#3B5A75'] },
    { id: 'meadow',   label: 'Meadow',   sub: 'Warm sage',  colors: ['#EFE9D9', '#A8C49A', '#2F5A3A'] },
    { id: 'dusk',     label: 'Dusk',     sub: 'Soft amber', colors: ['#F2E5D3', '#D9A24E', '#5C3A2A'] },
  ];
  const durations = [15, 20, 25, 30, 45, 60];
  const breaks = [3, 5, 10, 15];

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      background: T.bg, padding: '20px 24px 0', overflow: 'auto',
    }}>
      <div style={{ fontFamily: T.serif, fontSize: 30, color: T.ink, letterSpacing: -0.5 }}>Settings</div>
      <div style={{
        fontSize: 11, color: T.inkMute, marginTop: 2, letterSpacing: 0.4,
      }}>v2.4 · Synced 2 min ago</div>

      {/* Theme — picker cards */}
      <Section title="Appearance" hint="A calming visual to focus in">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
          {themes.map(th => {
            const on = theme === th.id;
            return (
              <button key={th.id} onClick={() => setTheme(th.id)} style={{
                background: T.paper, borderRadius: 12,
                border: `1.5px solid ${on ? T.moss : T.line}`,
                padding: 10, cursor: 'pointer', textAlign: 'left',
                display: 'flex', flexDirection: 'column', gap: 8,
                position: 'relative',
                boxShadow: on ? '0 1px 0 rgba(255,255,255,0.6) inset, 0 0 0 3px rgba(47,90,58,0.10)' : 'none',
              }}>
                {/* swatch */}
                <div style={{
                  height: 38, borderRadius: 8, overflow: 'hidden',
                  display: 'flex', position: 'relative',
                  background: th.colors[0],
                }}>
                  <div style={{
                    position: 'absolute', bottom: -6, left: -6,
                    width: 22, height: 22, borderRadius: '50%', background: th.colors[2],
                  }} />
                  <div style={{
                    position: 'absolute', top: 6, right: 6,
                    width: 14, height: 14, borderRadius: '50%', background: th.colors[1],
                  }} />
                </div>
                <div>
                  <div style={{ fontSize: 12, color: T.ink, fontWeight: 600 }}>{th.label}</div>
                  <div style={{ fontSize: 10, color: T.inkMute, marginTop: 1 }}>{th.sub}</div>
                </div>
                {on && (
                  <div style={{
                    position: 'absolute', top: 8, right: 8,
                    width: 16, height: 16, borderRadius: '50%',
                    background: T.moss, color: T.paper,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M5 12l4 4L19 6" />
                    </svg>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </Section>

      {/* Focus duration */}
      <Section title="Focus duration" hint="How long each Pomodoro lasts">
        <SegmentRow values={durations} value={focus} onChange={setFocus} suffix="min" />
      </Section>

      {/* Break duration */}
      <Section title="Break" hint="Short rest between sessions">
        <SegmentRow values={breaks} value={brk} onChange={setBrk} suffix="min" />
      </Section>

      {/* Sound */}
      <Section title="End sound">
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            { id: 'chime',  label: 'Chime' },
            { id: 'bowl',   label: 'Bowl'  },
            { id: 'birds',  label: 'Birds' },
            { id: 'silent', label: 'Silent' },
          ].map(s => {
            const on = sound === s.id;
            return (
              <button key={s.id} onClick={() => setSound(s.id)} style={{
                flex: 1, padding: '8px 0', borderRadius: 10,
                background: on ? T.ink : T.paper,
                color: on ? T.paper : T.ink,
                border: `1px solid ${on ? T.ink : T.line}`,
                fontSize: 11.5, fontWeight: 600, letterSpacing: 0.3,
                cursor: 'pointer',
              }}>{s.label}</button>
            );
          })}
        </div>
      </Section>

      {/* DND toggle row */}
      <div style={{
        marginTop: 14, marginBottom: 14,
        background: T.paper, borderRadius: 14,
        border: `1px solid ${T.line}`, boxShadow: T.card,
        padding: '12px 14px',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, color: T.ink, fontWeight: 600 }}>
            Do not disturb while focusing
          </div>
          <div style={{ fontSize: 11, color: T.inkMute, marginTop: 2 }}>
            Silence notifications during sessions
          </div>
        </div>
        <button onClick={() => setDND(!doNotDisturb)} style={{
          width: 40, height: 24, borderRadius: 999, position: 'relative',
          background: doNotDisturb ? T.moss : T.lineStr,
          border: 'none', cursor: 'pointer', transition: 'background 0.2s',
        }}>
          <div style={{
            position: 'absolute', top: 2, left: doNotDisturb ? 18 : 2,
            width: 20, height: 20, borderRadius: '50%',
            background: T.paper,
            boxShadow: '0 1px 3px rgba(31,42,33,0.2)',
            transition: 'left 0.2s',
          }} />
        </button>
      </div>
    </div>
  );
}

function Section({ title, hint, children }) {
  return (
    <div style={{ marginTop: 18 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{
          fontSize: 11, color: T.inkSoft, letterSpacing: 1, textTransform: 'uppercase', fontWeight: 600,
        }}>{title}</div>
        {hint && <div style={{ fontSize: 11, color: T.inkMute }}>{hint}</div>}
      </div>
      {children}
    </div>
  );
}

function SegmentRow({ values, value, onChange, suffix }) {
  return (
    <div style={{
      display: 'flex', padding: 3, borderRadius: 12,
      background: T.paper, border: `1px solid ${T.line}`,
    }}>
      {values.map(v => {
        const on = v === value;
        return (
          <button key={v} onClick={() => onChange(v)} style={{
            flex: 1, padding: '8px 0', borderRadius: 9,
            background: on ? T.ink : 'transparent',
            color: on ? T.paper : T.ink,
            border: 'none', cursor: 'pointer',
            fontSize: 12, fontWeight: 600,
            fontFamily: T.sans, letterSpacing: 0.2,
            fontVariantNumeric: 'tabular-nums',
          }}>
            <span style={{ fontFamily: on ? T.serif : T.sans, fontSize: on ? 14 : 12 }}>{v}</span>
            <span style={{ opacity: 0.6, fontSize: 10, marginLeft: 3 }}>{suffix}</span>
          </button>
        );
      })}
    </div>
  );
}

window.ScreenSettings = ScreenSettings;
