import React, { useMemo, useState } from 'react';
import './ReportApp.css';

const TEAM_SAMPLE = `{
  "team": "Aurora Platform",
  "period": "2026-03-01 to 2026-03-31",
  "summary": "Shipped the shared auth layer, stabilized deployments, and reduced incident time-to-recover.",
  "stats": {
    "velocity": 42,
    "bugs_closed": 18,
    "on_time_pct": 92
  },
  "highlights": [
    "Rolled out feature flags across three services",
    "Improved build time by 27%",
    "Launched the Q2 onboarding flow"
  ],
  "milestones": [
    { "title": "Auth service cutover", "status": "done", "date": "2026-03-08", "owner": "Nina" },
    { "title": "SLO dashboard", "status": "in_progress", "date": "2026-03-22", "owner": "Ravi" },
    { "title": "Data retention policy", "status": "blocked", "date": "2026-03-29", "owner": "Kim" }
  ],
  "risks": [
    { "title": "Legacy token migration", "impact": "high", "mitigation": "Staged rollout with fallback" },
    { "title": "Analytics pipeline lag", "impact": "medium", "mitigation": "Autoscale workers" }
  ],
  "members": [
    { "name": "Nina Park", "role": "Tech Lead", "focus": "Auth migration", "wins": ["Cutover completed", "Mentored two new hires"] },
    { "name": "Ravi Patel", "role": "Backend", "focus": "Observability", "wins": ["SLO alerts tuned"] },
    { "name": "Kim Lee", "role": "Platform", "focus": "Policy + compliance", "wins": ["Drafted retention plan"] }
  ]
}`;

const INDIVIDUAL_SAMPLE = `{
  "name": "Alex Morgan",
  "role": "Product Designer",
  "period": "2026-03-01 to 2026-03-31",
  "summary": "Clarified the new invite flow and reduced drop-off in the scheduling funnel.",
  "metrics": {
    "design_reviews": 6,
    "experiments": 3,
    "handoffs": 4
  },
  "goals": [
    "Ship the invitation recap screen",
    "Improve accessibility for keyboard users"
  ],
  "tasks": [
    { "title": "Prototype invite recap", "status": "done", "impact": "high", "notes": "Validated with 5 users" },
    { "title": "Refine empty states", "status": "in_progress", "impact": "medium", "notes": "Needs copy review" },
    { "title": "Accessibility audit", "status": "blocked", "impact": "high", "notes": "Waiting on tooling" }
  ],
  "collaboration": [
    "Partnered with FE on motion guidelines",
    "Worked with QA on usability checks"
  ],
  "next": [
    "Finalize visual QA",
    "Ship invite recap to beta users"
  ]
}`;

const toLabel = (value) => value.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase());

function ReportApp() {
  const [mode, setMode] = useState('team');
  const [inputs, setInputs] = useState({
    team: TEAM_SAMPLE,
    individual: INDIVIDUAL_SAMPLE,
  });
  const [parseError, setParseError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [taskFilter, setTaskFilter] = useState('all');
  const [taskSearch, setTaskSearch] = useState('');

  const currentInput = inputs[mode];

  const parsedData = useMemo(() => {
    try {
      const parsed = JSON.parse(currentInput);
      setParseError('');
      return parsed;
    } catch (error) {
      setParseError('Invalid JSON. Please fix formatting to preview the report.');
      return null;
    }
  }, [currentInput]);

  const updateInput = (value) => {
    setInputs((prev) => ({ ...prev, [mode]: value }));
  };

  const loadSample = () => {
    setInputs((prev) => ({
      ...prev,
      [mode]: mode === 'team' ? TEAM_SAMPLE : INDIVIDUAL_SAMPLE,
    }));
  };

  const filteredTasks = useMemo(() => {
    if (!parsedData?.tasks) return [];
    return parsedData.tasks.filter((task) => {
      const matchesStatus = taskFilter === 'all' || task.status === taskFilter;
      const matchesSearch = task.title.toLowerCase().includes(taskSearch.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [parsedData, taskFilter, taskSearch]);

  return (
    <div className="report-app">
      <div className="report-bg" />
      <header className="hero">
        <div>
          <p className="eyebrow">Interactive Report Console</p>
          <h1>Team + Individual Reports from JSON</h1>
          <p className="subtitle">
            Paste JSON on the left, get a polished, share-ready report on the right.
          </p>
        </div>
        <div className="mode-toggle">
          <button
            className={mode === 'team' ? 'active' : ''}
            onClick={() => {
              setMode('team');
              setActiveTab('overview');
            }}
          >
            Team Report
          </button>
          <button
            className={mode === 'individual' ? 'active' : ''}
            onClick={() => {
              setMode('individual');
              setActiveTab('overview');
            }}
          >
            Individual Report
          </button>
        </div>
      </header>

      <main className="report-grid">
        <section className="panel input-panel">
          <div className="panel-header">
            <h2>JSON Input</h2>
            <div className="panel-actions">
              <button className="ghost" onClick={loadSample}>Load Sample</button>
            </div>
          </div>
          <textarea
            className="json-input"
            value={currentInput}
            onChange={(e) => updateInput(e.target.value)}
            spellCheck={false}
          />
          {parseError && <p className="error-text">{parseError}</p>}
          <div className="hint">
            Use the sample structure as a guide. Extra fields are ignored.
          </div>
        </section>

        <section className="panel output-panel">
          <div className="panel-header">
            <h2>Report Preview</h2>
            <div className="tabs">
              <button
                className={activeTab === 'overview' ? 'active' : ''}
                onClick={() => setActiveTab('overview')}
              >
                Overview
              </button>
              <button
                className={activeTab === 'details' ? 'active' : ''}
                onClick={() => setActiveTab('details')}
              >
                Details
              </button>
              <button
                className={activeTab === 'next' ? 'active' : ''}
                onClick={() => setActiveTab('next')}
              >
                Next Steps
              </button>
            </div>
          </div>

          {!parsedData && (
            <div className="empty-state">
              <h3>Waiting on valid JSON</h3>
              <p>Fix the JSON on the left to see the report update live.</p>
            </div>
          )}

          {parsedData && mode === 'team' && (
            <div className="report-body">
              <section className="report-header">
                <div>
                  <h3>{parsedData.team}</h3>
                  <p className="meta">{parsedData.period}</p>
                </div>
                <div className="chip-row">
                  {(parsedData.highlights || []).slice(0, 2).map((item) => (
                    <span key={item} className="chip">{item}</span>
                  ))}
                </div>
              </section>

              {activeTab === 'overview' && (
                <>
                  <div className="summary-card">
                    <h4>Summary</h4>
                    <p>{parsedData.summary}</p>
                  </div>

                  <div className="stat-grid">
                    {parsedData.stats &&
                      Object.entries(parsedData.stats).map(([key, value]) => (
                        <div key={key} className="stat-card">
                          <p className="stat-label">{toLabel(key)}</p>
                          <p className="stat-value">{value}</p>
                        </div>
                      ))}
                  </div>

                  <div className="list-card">
                    <h4>Highlights</h4>
                    <div className="list">
                      {(parsedData.highlights || []).map((item) => (
                        <div key={item} className="list-item">{item}</div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'details' && (
                <>
                  <div className="list-card">
                    <h4>Milestones</h4>
                    <div className="card-list">
                      {(parsedData.milestones || []).map((item) => (
                        <div key={item.title} className="row-card">
                          <div>
                            <p className="row-title">{item.title}</p>
                            <p className="meta">{item.owner} · {item.date}</p>
                          </div>
                          <span className={`status ${item.status}`}>{toLabel(item.status)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="list-card">
                    <h4>Risks</h4>
                    <div className="card-list">
                      {(parsedData.risks || []).map((item) => (
                        <div key={item.title} className="row-card">
                          <div>
                            <p className="row-title">{item.title}</p>
                            <p className="meta">{item.mitigation}</p>
                          </div>
                          <span className={`impact ${item.impact}`}>{toLabel(item.impact)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'next' && (
                <div className="list-card">
                  <h4>Team Focus</h4>
                  <div className="card-list">
                    {(parsedData.members || []).map((member) => (
                      <div key={member.name} className="member-card">
                        <div>
                          <p className="row-title">{member.name}</p>
                          <p className="meta">{member.role} · {member.focus}</p>
                        </div>
                        <div className="chip-row">
                          {(member.wins || []).map((win) => (
                            <span key={win} className="chip chip-soft">{win}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {parsedData && mode === 'individual' && (
            <div className="report-body">
              <section className="report-header">
                <div>
                  <h3>{parsedData.name}</h3>
                  <p className="meta">{parsedData.role} · {parsedData.period}</p>
                </div>
                <div className="chip-row">
                  {(parsedData.goals || []).slice(0, 2).map((item) => (
                    <span key={item} className="chip">{item}</span>
                  ))}
                </div>
              </section>

              {activeTab === 'overview' && (
                <>
                  <div className="summary-card">
                    <h4>Summary</h4>
                    <p>{parsedData.summary}</p>
                  </div>

                  <div className="stat-grid">
                    {parsedData.metrics &&
                      Object.entries(parsedData.metrics).map(([key, value]) => (
                        <div key={key} className="stat-card">
                          <p className="stat-label">{toLabel(key)}</p>
                          <p className="stat-value">{value}</p>
                        </div>
                      ))}
                  </div>

                  <div className="list-card">
                    <h4>Goals</h4>
                    <div className="list">
                      {(parsedData.goals || []).map((item) => (
                        <div key={item} className="list-item">{item}</div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'details' && (
                <>
                  <div className="task-filters">
                    <input
                      className="task-search"
                      value={taskSearch}
                      onChange={(e) => setTaskSearch(e.target.value)}
                      placeholder="Search tasks"
                    />
                    <select
                      className="task-select"
                      value={taskFilter}
                      onChange={(e) => setTaskFilter(e.target.value)}
                    >
                      <option value="all">All</option>
                      <option value="done">Done</option>
                      <option value="in_progress">In Progress</option>
                      <option value="blocked">Blocked</option>
                    </select>
                  </div>

                  <div className="card-list">
                    {filteredTasks.map((task) => (
                      <div key={task.title} className="task-card">
                        <div>
                          <p className="row-title">{task.title}</p>
                          <p className="meta">{task.notes}</p>
                        </div>
                        <div className="chip-row">
                          <span className={`status ${task.status}`}>{toLabel(task.status)}</span>
                          <span className={`impact ${task.impact}`}>{toLabel(task.impact)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {activeTab === 'next' && (
                <div className="list-card">
                  <h4>Next Steps</h4>
                  <div className="list">
                    {(parsedData.next || []).map((item) => (
                      <div key={item} className="list-item">{item}</div>
                    ))}
                  </div>
                  <div className="list-card nested">
                    <h4>Collaboration</h4>
                    <div className="list">
                      {(parsedData.collaboration || []).map((item) => (
                        <div key={item} className="list-item">{item}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default ReportApp;
