import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BarChart3, Boxes, LogOut, MessageSquare, ShieldCheck, TrendingUp } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function generateRandomHex(bytes) {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return Array.from(arr, (b) => b.toString(16).padStart(2, '0')).join('');
}

function generateTraceparent() {
  const traceId = generateRandomHex(16); // 32 hex chars
  const spanId = generateRandomHex(8);   // 16 hex chars
  return `00-${traceId}-${spanId}-01`;
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled UI Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="login-shell">
          <div className="login-card" style={{ maxWidth: '480px', textAlign: 'center' }}>
            <h2>Something went wrong</h2>
            <p className="muted">An unexpected client-side error occurred.</p>
            <div className="error" style={{ textAlign: 'left', wordBreak: 'break-word', fontFamily: 'monospace' }}>
              {this.state.error?.message || String(this.state.error)}
            </div>
            <button className="primary" onClick={() => window.location.reload()} style={{ marginTop: '1rem' }}>
              Reload Application
            </button>
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}

const api = async (path, options = {}) => {
  const traceparent = generateTraceparent();
  const requestId = `req-${generateRandomHex(6)}`;

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Request-ID': requestId,
      'traceparent': traceparent,
      ...(options.headers || {}),
      ...(localStorage.getItem('token')
        ? { Authorization: `Bearer ${localStorage.getItem('token')}` }
        : {}),
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody.detail || 'Request failed';
    const serverReqId = response.headers.get('X-Request-ID') || requestId;
    const error = new Error(`${message} (Request ID: ${serverReqId})`);
    error.requestId = serverReqId;
    error.status = response.status;
    throw error;
  }

  return response.json();
};

function Login({ onLogin }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const submit = async (event) => {
    event.preventDefault();
    setError('');

    if (!form.username || !form.password) {
      return setError('Enter a username and password.');
    }

    try {
      const data = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      localStorage.setItem('token', data.access_token);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-art">
        <span className="eyebrow">BUNNY / OPERATIONS</span>
        <h1>
          Make the work
          <br />
          <em>visible.</em>
        </h1>
        <p>A clear starting point for products, support, and sales.</p>
      </section>
      <form className="login-card" onSubmit={submit}>
        <div className="mark">
          <ShieldCheck size={20} /> Secure sign in
        </div>
        <h2>Welcome back</h2>
        <p className="muted">Use a seeded account to explore the workspace.</p>
        <label>
          Username
          <input
            autoFocus
            value={form.username}
            onChange={(event) =>
              setForm({ ...form, username: event.target.value })
            }
            placeholder="manager"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={(event) =>
              setForm({ ...form, password: event.target.value })
            }
            placeholder="••••••"
          />
        </label>
        {error && <div className="error">{error}</div>}
        <button className="primary">
          Enter workspace <TrendingUp size={17} />
        </button>
        <small>
          Manager: manager / reganam
          <br />
          Worker: worker / rekrow
        </small>
      </form>
    </main>
  );
}

function App({ user, onLogout }) {
  const [products, setProducts] = useState([]);
  const [requests, setRequests] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState(() => window.location.pathname.slice(1) || 'overview');

  useEffect(() => {
    const handleNavigation = () => setTab(window.location.pathname.slice(1) || 'overview');
    window.addEventListener('popstate', handleNavigation);
    return () => window.removeEventListener('popstate', handleNavigation);
  }, []);

  const navigate = (nextTab) => {
    window.history.pushState({}, '', `/${nextTab}`);
    setTab(nextTab);
  };

  useEffect(() => {
    api(`/products?search=${encodeURIComponent(search)}`).then(setProducts);
    api('/support-requests').then(setRequests);
    if (user.role === 'manager') {
      api('/metrics/summary').then(setMetrics);
    }
  }, [search, user.role]);

  const nav = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'products', label: 'Products', icon: Boxes },
    { id: 'support', label: 'Support queue', icon: MessageSquare },
  ];

  return (
    <div className="app-shell">
      <aside>
        <div className="brand">
          <span>✦</span> bunny
        </div>
        <div className="workspace-label">Workspace</div>
        {nav.map((item) => (
          <button
            className={tab === item.id ? 'nav active' : 'nav'}
            onClick={() => navigate(item.id)}
            key={item.id}
          >
            <item.icon size={18} />
            {item.label}
          </button>
        ))}
        <div className="aside-bottom">
          <div className="user-chip">
            <div className="avatar">{user.username[0].toUpperCase()}</div>
            <div>
              <strong>{user.username}</strong>
              <small>{user.role}</small>
            </div>
          </div>
          <button className="nav" onClick={onLogout}>
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </aside>
      <main className="content">
        <header>
          <div>
            <span className="eyebrow">MONDAY, SEPTEMBER 03, 2026</span>
            <h1>
              {tab === 'overview' ? 'Good morning, ' : ''}
              <em>
                {tab === 'overview'
                  ? user.username
                  : nav.find((item) => item.id === tab).label}
              </em>
            </h1>
          </div>
          <div className="status-dot">● Live data</div>
        </header>
        {tab === 'overview' && user.role === 'manager' && (
          <Overview metrics={metrics} />
        )}
        {tab === 'overview' && user.role !== 'manager' && <WorkerIntro />}
        {tab === 'products' && (
          <Table
            title="Product catalogue"
            items={products}
            search={search}
            setSearch={setSearch}
          />
        )}
        {tab === 'support' && <SupportTable items={requests} />}
      </main>
    </div>
  );
}

function Overview({ metrics }) {
  if (!metrics) return <p>Loading workspace...</p>;

  const metricItems = [
    ['Revenue', `$${metrics.revenue.toLocaleString()}`, 'all time'],
    ['Units sold', metrics.sales_count, 'across products'],
    ['Open requests', metrics.open_requests, 'needs attention'],
    [
      'Avg. resolution',
      `${metrics.average_resolution_days}d`,
      'resolved requests',
    ],
  ];

  return (
    <>
      <section className="metrics">
        {metricItems.map(([label, value, note]) => (
          <article className="metric" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{note}</small>
          </article>
        ))}
      </section>
      <section className="dashboard-grid">
        <article className="panel chart-panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">REVENUE MIX</span>
              <h2>Revenue by product</h2>
            </div>
            <TrendingUp size={20} />
          </div>
          <div className="bars">
            {Object.entries(metrics.revenue_by_product).map(([name, value]) => (
              <div className="bar-row" key={name}>
                <span>{name}</span>
                <div>
                  <i
                    style={{
                      width: `${Math.max(8, (value / metrics.revenue) * 100)}%`,
                    }}
                  />
                </div>
                <b>${value.toLocaleString()}</b>
              </div>
            ))}
          </div>
        </article>
        <article className="panel note-panel">
          <span className="eyebrow">OPERATIONS NOTE</span>
          <h2>Keep the queue moving.</h2>
          <p>
            There are {metrics.open_requests} requests currently open. The 95th
            percentile resolution time is {metrics.p95_resolution_days} days.
          </p>
          <button className="text-button">Review support queue →</button>
        </article>
      </section>
    </>
  );
}

function WorkerIntro() {
  return (
    <section className="worker-welcome">
      <span className="eyebrow">YOUR WORKSPACE</span>
      <h2>
        Products and support,
        <br />
        <em>in one calm view.</em>
      </h2>
      <p>
        Browse the catalogue or keep an eye on the active support queue. Sales
        and financial metrics are available to managers.
      </p>
    </section>
  );
}

function Table({ title, items, search, setSearch }) {
  return (
    <section className="panel table-panel">
      <div className="panel-head">
        <div>
          <span className="eyebrow">CATALOGUE</span>
          <h2>{title}</h2>
        </div>
        <input
          className="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search products"
        />
      </div>
      <table>
        <thead>
          <tr>
            <th>Product</th>
            <th>Category</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>{item.name}</strong>
              </td>
              <td>
                <span className="tag">{item.category}</span>
              </td>
              <td>${item.price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function SupportTable({ items }) {
  return (
    <section className="panel table-panel">
      <div className="panel-head">
        <div>
          <span className="eyebrow">CUSTOMER CARE</span>
          <h2>Support queue</h2>
        </div>
        <span className="count">{items.length} requests</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Request</th>
            <th>Product</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <strong>{item.title}</strong>
              </td>
              <td>{item.product_name}</td>
              <td>
                <span className={`status ${item.status}`}>{item.status}</span>
              </td>
              <td>{new Date(item.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function Root() {
  const [user, setUser] = useState(null);
  const token = localStorage.getItem('token');
  const [checkingSession, setCheckingSession] = useState(Boolean(token));

  useEffect(() => {
    if (!token) return;
    api('/auth/me')
      .then(setUser)
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setCheckingSession(false));
  }, [token]);

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (checkingSession) return <main className="session-check">Checking session...</main>;
  return user ? <App user={user} onLogout={logout} /> : <Login onLogin={setUser} />;
}

createRoot(document.getElementById('root')).render(
  <ErrorBoundary>
    <Root />
  </ErrorBoundary>
);