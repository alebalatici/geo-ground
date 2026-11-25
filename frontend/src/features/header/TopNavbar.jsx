import { Link, useLocation } from 'react-router-dom';
import { HEADER_CONTENT } from '../../config/appContent.js';
import ThemeToggleButton from './ThemeToggleButton.jsx';
import './navbar.css';

const VIEW_OPTIONS = [
  { value: 'executive', label: HEADER_CONTENT.viewSwitcher.executiveLabel },
  { value: 'enterprise', label: HEADER_CONTENT.viewSwitcher.enterpriseLabel },
];

function DataBadge({ dataSource, isLoading, hasData }) {
  const state = isLoading ? 'loading' : dataSource === 'api' && hasData ? 'live' : 'demo';
  const label = HEADER_CONTENT.dataSourceBadge[state];
  const tooltip = state === 'loading'
    ? HEADER_CONTENT.dataSourceBadge.loadingTooltip
    : state === 'live'
      ? 'Monitored site data loaded from the backend API. Satellite observation timing depends on the available dataset.'
      : HEADER_CONTENT.dataSourceBadge.demoTooltip;
  return <span className={`data-badge data-badge--${state}`} title={tooltip} role="status" aria-live="polite"><span className="data-badge__label">{label}</span></span>;
}

export default function TopNavbar({
  variant = 'dashboard',
  viewMode = 'executive',
  onViewModeChange,
  dataSource = 'mock',
  isLoading = false,
  sites = [],
  selectedSiteId = '',
  onSelectSite,
  onSignIn,
}) {
  const location = useLocation();
  const isLanding = variant === 'landing';
  const selectedSite = sites.find((site) => String(site.id) === String(selectedSiteId));
  const selectorLabel = isLoading
    ? 'Loading monitored sites…'
    : sites.length === 0
      ? dataSource === 'mock' ? 'Demo sites unavailable' : 'No monitored sites'
      : 'Select a site';

  function handleSectionLink(event, targetId) {
    if (isLanding && location.pathname === '/') {
      const target = document.getElementById(targetId);
      if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  return (
    <header className={`top-navbar${isLanding ? ' top-navbar--landing' : ''}`}>
      <div className="top-navbar__inner">
        <div className="top-navbar__left">
          <Link to="/" className="top-navbar__brand" aria-label="GeoGround home">
            <span className="top-navbar__brand-mark" aria-hidden="true" />GeoGround
          </Link>
          {!isLanding && <DataBadge dataSource={dataSource} isLoading={isLoading} hasData={sites.length > 0} />}
        </div>
        {isLanding ? (
          <nav className="top-navbar__links top-navbar__links--landing" aria-label="Landing page navigation">
            <a className="top-navbar__link" href="#plans" onClick={(event) => handleSectionLink(event, 'plans')}>Plans</a>
            <a className="top-navbar__link" href="#mission" onClick={(event) => handleSectionLink(event, 'mission')}>Our Mission</a>
          </nav>
        ) : (
          <div className="top-navbar__center">
            <div className="view-switcher" role="group" aria-label={HEADER_CONTENT.viewSwitcher.ariaLabel}>
              {VIEW_OPTIONS.map((option) => <button key={option.value} type="button" className={`view-switcher__button${viewMode === option.value ? ' view-switcher__button--active' : ''}`} aria-pressed={viewMode === option.value} onClick={() => onViewModeChange?.(option.value)}>{option.label}</button>)}
            </div>
            <label className="site-selector"><span className="visually-hidden">Monitored site</span><select aria-label="Select monitored site" value={selectedSite ? String(selectedSite.id) : ''} onChange={(event) => { const site = sites.find((item) => String(item.id) === event.target.value); if (site) onSelectSite?.(site.id); }} disabled={isLoading || sites.length === 0}><option value="" disabled>{selectorLabel}</option>{sites.map((site) => <option key={site.id} value={String(site.id)}>{site.name}</option>)}</select><span className="site-selector__chevron" aria-hidden="true">⌄</span></label>
          </div>
        )}
        <div className="top-navbar__right">
          <ThemeToggleButton />
          <button className="navbar-sign-in" type="button" onClick={onSignIn}>Sign In</button>
        </div>
      </div>
    </header>
  );
}
