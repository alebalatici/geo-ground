/** True when the visitor asked the system to reduce motion. */
export function prefersReducedMotion() {
  return (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}

/**
 * Scrolls smoothly to the element with the given id.
 * Returns true if the element exists, false otherwise.
 */
export function scrollToSection(targetId) {
  const targetElement = document.getElementById(targetId);
  if (!targetElement) {
    return false;
  }
  targetElement.scrollIntoView({
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
    block: 'start',
  });
  return true;
}

/** Scrolls smoothly to the very top of the page. */
export function scrollToTop() {
  window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
}