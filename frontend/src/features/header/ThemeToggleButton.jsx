import { HEADER_CONTENT } from '../../config/appContent.js';
import { useTheme } from '../../context/ThemeContext.jsx';

function SunIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

export default function ThemeToggleButton() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  const { ariaLabel, switchToLightTooltip, switchToDarkTooltip } = HEADER_CONTENT.themeToggle;
  const tooltip = isDark ? switchToLightTooltip : switchToDarkTooltip;

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={toggleTheme}
      aria-label={`${ariaLabel} — ${tooltip}`}
      title={tooltip}
    >
      <span key={theme} className="theme-toggle__icon">
        {isDark ? <SunIcon /> : <MoonIcon />}
      </span>
    </button>
  );
}