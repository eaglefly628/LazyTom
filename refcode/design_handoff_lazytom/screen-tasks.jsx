// LazyTom — Tasks screen (redesigned)

function ScreenTasks() {
  const [sort, setSort] = React.useState('hard');
  const [diff, setDiff] = React.useState(2); // 0..4
  const [duration, setDuration] = React.useState(25);
  const [task, setTask] = React.useState('');

  const diffs = [
    { label: 'Very Easy', short: 'V.Easy', color: T.sky },
    { label: 'Easy',      short: 'Easy',   color: T.leaf },
    { label: 'Normal',    short: 'Normal', color: T.mossSoft },
    { label: 'Hard',      short: 'Hard',   color: T.amber },
    { label: 'Very Hard', short: 'V.Hard', color: T.rose },
  ];
  const durations = [5, 10, 15, 20, 25, 30, 45, 60];

  const tasks = [
    { title: 'Chinese essay — first draft', diff: 4, mins: 45, suggested: true },
    { title: 'Math homework Ch. 7',         diff: 3, mins: 25 },
    { title: 'English reading log',         diff: 1, mins: 20 },
  ];

  const templates = [
    { name: 'Math Homework',     mins: 25, diff: 3 },
    { name: 'Chinese Essay',     mins: 45, diff: 4 },
    { name: 'English Reading',   mins: 20, diff: 1 },
    { name: 'Science Lab',       mins: 30, diff: 3 },
    { name: 'Piano Practice',    mins: 20, diff: 2 },
    { name: 'Art Project',       mins: 30, diff: 2 },
  ];

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      background: T.bg, padding: '20px 24px 0', overflow: 'hidden',
    }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div style={{ fontFamily: T.serif, fontSize: 30, color: T.ink, letterSpacing: -0.5 }}>Tasks</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: T.inkMute, fontWeight: 500, letterSpacing: 0.4 }}>
          <span style={{ width: 6, height: 6, borderRadius: 3, background: T.clay }} />
          {tasks.length} pending · 1h 30m
        </div>
      </div>

      {/* Smart pick hero — the one task to do now */}
      <div style={{
        marginTop: 14,
        background: T.paper, borderRadius: 16,
        border: `1px solid ${T.line}`, boxShadow: T.card,
        padding: '14px 16px 16px',
        position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.clay} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" />
            <circle cx="12" cy="12" r="4" fill={T.clay} stroke="none" />
          </svg>
          <div style={{ fontSize: 10.5, color: T.clay, letterSpacing: 1.4, textTransform: 'uppercase', fontWeight: 600 }}>
            Start with this
          </div>
          <div style={{ flex: 1 }} />
          <div style={{ fontSize: 10, color: T.inkMute, fontWeight: 500 }}>HARD FIRST</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 12, marginTop: 8 }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: T.serif, fontSize: 22, color: T.ink, lineHeight: 1.15, letterSpacing: -0.3 }}>
              Chinese essay<br />— first draft
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
              <span style={{
                fontSize: 10, color: T.rose, fontWeight: 600, letterSpacing: 0.5,
                padding: '3px 8px', borderRadius: 999, background: 'rgba(184,90,90,0.10)',
              }}>VERY HARD</span>
              <span style={{ fontSize: 11, color: T.inkSoft, fontWeight: 500 }}>45 min · +5 pts</span>
            </div>
          </div>
          <button style={{
            width: 52, height: 52, borderRadius: '50%',
            background: T.moss, color: '#F7F2E4', border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer', boxShadow: T.press, flexShrink: 0,
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l14 8-14 8V4z" /></svg>
          </button>
        </div>
      </div>

      {/* Sort segmented control */}
      <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ fontSize: 11, color: T.inkMute, letterSpacing: 1, textTransform: 'uppercase', fontWeight: 600 }}>
          Order
        </div>
        <div style={{
          display: 'flex', padding: 3, borderRadius: 999,
          background: T.paper, border: `1px solid ${T.line}`,
        }}>
          {['easy', 'hard', 'manual'].map(k => (
            <button key={k} onClick={() => setSort(k)} style={{
              padding: '5px 12px', borderRadius: 999,
              fontSize: 11.5, fontWeight: 600, letterSpacing: 0.3,
              border: 'none', cursor: 'pointer',
              background: sort === k ? T.ink : 'transparent',
              color: sort === k ? T.paper : T.inkSoft,
            }}>
              {k === 'easy' ? 'Easy first' : k === 'hard' ? 'Hard first' : 'Manual'}
            </button>
          ))}
        </div>
      </div>

      {/* Task list */}
      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column' }}>
        {tasks.map((t, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '11px 4px',
            borderBottom: i < tasks.length - 1 ? `1px solid ${T.line}` : 'none',
            opacity: t.suggested ? 0.5 : 1,
          }}>
            <div style={{
              width: 18, height: 18, borderRadius: 5,
              border: `1.5px solid ${T.lineStr}`, background: T.paper,
              flexShrink: 0,
            }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13.5, color: T.ink, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {t.title}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 3 }}>
                <span style={{
                  width: 6, height: 6, borderRadius: 3,
                  background: diffs[t.diff].color,
                }} />
                <span style={{ fontSize: 10.5, color: T.inkMute, fontWeight: 500, letterSpacing: 0.3 }}>
                  {diffs[t.diff].label} · {t.mins} min
                </span>
              </div>
            </div>
            <button style={{
              width: 28, height: 28, borderRadius: '50%',
              border: `1px solid ${T.lineStr}`, background: 'transparent',
              color: T.inkSoft, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l14 8-14 8V4z" /></svg>
            </button>
          </div>
        ))}
      </div>

      {/* Add a task composer */}
      <div style={{
        marginTop: 14, marginBottom: 14,
        background: T.paper, borderRadius: 14,
        border: `1px solid ${T.line}`, boxShadow: T.card,
        padding: 12,
      }}>
        {/* template chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
          <div style={{ fontSize: 10, color: T.inkMute, fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase' }}>
            Templates
          </div>
          <div style={{ flex: 1, height: 1, background: T.line }} />
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 12 }}>
          {templates.map((t, i) => (
            <button key={i} style={{
              padding: '5px 10px', borderRadius: 999,
              background: T.bg, border: `1px solid ${T.line}`,
              fontSize: 11, color: T.inkSoft, fontWeight: 500,
              display: 'inline-flex', alignItems: 'center', gap: 6, cursor: 'pointer',
            }}>
              <span style={{ width: 6, height: 6, borderRadius: 3, background: diffs[t.diff].color }} />
              {t.name}
              <span style={{ color: T.inkMute, fontVariantNumeric: 'tabular-nums' }}>{t.mins}m</span>
            </button>
          ))}
        </div>

        {/* difficulty + duration selectors */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ fontSize: 10.5, color: T.inkMute, width: 56, fontWeight: 600, letterSpacing: 0.5 }}>
              DIFFICULTY
            </div>
            <div style={{ display: 'flex', flex: 1, gap: 4 }}>
              {diffs.map((d, i) => (
                <button key={i} onClick={() => setDiff(i)} style={{
                  flex: 1, padding: '5px 4px', borderRadius: 6,
                  background: diff === i ? d.color : 'transparent',
                  border: `1px solid ${diff === i ? d.color : T.line}`,
                  fontSize: 10, color: diff === i ? '#F7F2E4' : T.inkSoft,
                  fontWeight: 600, letterSpacing: 0.3, cursor: 'pointer',
                }}>
                  {d.short}
                </button>
              ))}
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ fontSize: 10.5, color: T.inkMute, width: 56, fontWeight: 600, letterSpacing: 0.5 }}>
              DURATION
            </div>
            <div style={{ display: 'flex', flex: 1, gap: 4 }}>
              {durations.map(d => (
                <button key={d} onClick={() => setDuration(d)} style={{
                  flex: 1, padding: '5px 0', borderRadius: 6,
                  background: duration === d ? T.ink : 'transparent',
                  border: `1px solid ${duration === d ? T.ink : T.line}`,
                  fontSize: 10.5, color: duration === d ? T.paper : T.inkSoft,
                  fontWeight: 600, letterSpacing: 0.2, cursor: 'pointer',
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  {d}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* input */}
        <div style={{
          marginTop: 10, display: 'flex', alignItems: 'center', gap: 8,
          background: T.bg, borderRadius: 10, padding: '8px 8px 8px 12px',
          border: `1px solid ${T.line}`,
        }}>
          <input value={task} onChange={e => setTask(e.target.value)}
            placeholder="What needs doing?" style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              fontSize: 13, color: T.ink, fontFamily: T.sans,
            }} />
          <button style={{
            width: 30, height: 30, borderRadius: '50%',
            background: T.moss, color: '#F7F2E4', border: 'none',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
          }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

window.ScreenTasks = ScreenTasks;
