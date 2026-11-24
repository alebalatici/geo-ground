import { HEADER_CONTENT } from '../../config/appContent.js';
import { scrollToSection, scrollToTop } from '../../utils/scrollHelpers.js';
import ThemeToggleButton from './ThemeToggleButton.jsx';
import './navbar.css';

const VIEW_OPTIONS = [
  { value: 'executive', label: HEADER_CONTENT.viewSwitcher.executiveLabel },
  { value: 'enterprise', label: HEADER_CONTENT.viewSwitcher.enterpriseLabel },
];

/*
function resolveBadgeState(dataSource, isLoading) {
  if (isLoading) return 'loading';
  return dataSource === 'api' ? 'live' : 'demo';
}*/

export default function TopNavbar({
  viewMode,
  onViewModeChange,
  // dataSource,
  // isLoading = false,
  authSlot = null,
}) {
  /*
   const badgeCopy = HEADER_CONTENT.dataSourceBadge;
   const badgeState = resolveBadgeState(dataSource, isLoading);
   const badgeLabel = badgeCopy[badgeState];
   const badgeTooltip = badgeCopy[`${badgeState}Tooltip`];
*/

  function handleNavLinkClick(event, targetId) {
    if (scrollToSection(targetId)) {
      event.preventDefault();
    }
  }

  function handleBrandClick(event) {
    event.preventDefault();
    scrollToTop();
  }

  return (
    <header className="top-navbar">
      <div className="top-navbar__inner">
        <div className="top-navbar__left">
          <a
            href="#top"
            className="top-navbar__brand"
            onClick={handleBrandClick}
            aria-label={HEADER_CONTENT.brandAriaLabel}
          >
            <span className="top-navbar__brand-mark" aria-hidden="true" />
            {HEADER_CONTENT.brandName}
          </a>

          {/*
          <span
            className={`data-badge data-badge--${badgeState}`}
            title={badgeTooltip}
          >
            <span className="data-badge__label">{badgeLabel}</span>
          </span> */}
        </div>

        <div className="top-navbar__center">
          <nav className="top-navbar__links" aria-label={HEADER_CONTENT.navAriaLabel}>
            {HEADER_CONTENT.navLinks.map((link) => (
              <a
                key={link.targetId}
                href={`#${link.targetId}`}
                className="top-navbar__link"
                onClick={(event) => handleNavLinkClick(event, link.targetId)}
              >
                {link.label}
              </a>
            ))}
          </nav>

          <div
            className="view-switcher"
            role="group"
            aria-label={HEADER_CONTENT.viewSwitcher.ariaLabel}
          >
            {VIEW_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                className={`view-switcher__button${
                  viewMode === option.value ? ' view-switcher__button--active' : ''
                }`}
                aria-pressed={viewMode === option.value}
                onClick={() => onViewModeChange(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="top-navbar__right">
          <ThemeToggleButton />
          <div
            className="top-navbar__auth-slot"
            role="group"
            aria-label={HEADER_CONTENT.authSlot.ariaLabel}
          >
            {authSlot}
          </div>
        </div>
      </div>
    </header>
  );
}