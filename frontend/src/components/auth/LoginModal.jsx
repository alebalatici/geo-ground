import { useEffect, useRef, useState } from 'react';
import './loginModal.css';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function EyeIcon({ hidden }) {
  return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M2.5 12s3.3-6 9.5-6 9.5 6 9.5 6-3.3 6-9.5 6-9.5-6-9.5-6Z" />
    <circle cx="12" cy="12" r="2.7" />
    {hidden && <path d="m4 4 16 16" />}
  </svg>;
}

function validate(email, password) {
  const errors = {};
  if (!email.trim()) errors.email = 'Please enter your email address.';
  else if (!EMAIL_PATTERN.test(email.trim())) errors.email = 'Please enter a valid email address.';
  if (!password) errors.password = 'Please enter your password.';
  return errors;
}

export default function LoginModal({ open, onClose }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState({});
  const [notice, setNotice] = useState('');
  const [closing, setClosing] = useState(false);
  const dialogRef = useRef(null);
  const emailRef = useRef(null);
  const passwordRef = useRef(null);
  const closeTimer = useRef(null);
  const opener = useRef(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (!open) return undefined;
    if (!wasOpen.current) opener.current = document.activeElement;
    wasOpen.current = true;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const focusTimer = window.requestAnimationFrame(() => emailRef.current?.focus());

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        requestClose();
      }
      if (event.key !== 'Tab') return;
      const items = [...(dialogRef.current?.querySelectorAll('button:not(:disabled), a[href], input:not(:disabled)') || [])];
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      window.cancelAnimationFrame(focusTimer);
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
    // onClose is intentionally invoked by the event listener; reopening resets focus and the animation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  useEffect(() => () => window.clearTimeout(closeTimer.current), []);

  function requestClose() {
    if (closing) return;
    setClosing(true);
    closeTimer.current = window.setTimeout(() => {
      setEmail('');
      setPassword('');
      setShowPassword(false);
      setRememberMe(false);
      setErrors({});
      setNotice('');
      setClosing(false);
      wasOpen.current = false;
      onClose?.();
      window.requestAnimationFrame(() => opener.current?.focus?.());
    }, 180);
  }

  function handleSubmit(event) {
    event.preventDefault();
    const nextErrors = validate(email, password);
    setErrors(nextErrors);
    setNotice('');
    if (Object.keys(nextErrors).length) {
      (nextErrors.email ? emailRef : passwordRef).current?.focus();
      return;
    }
    // No authentication endpoint is available; credentials remain in this component and are never transmitted.
    setNotice('Sign-in is unavailable in this preview.');
  }

  if (!open) return null;
  return (
    <div className={`login-overlay${closing ? ' login-overlay--closing' : ''}`} onMouseDown={(event) => { if (event.target === event.currentTarget) requestClose(); }}>
      <section ref={dialogRef} className="login-dialog" role="dialog" aria-modal="true" aria-labelledby="login-title" aria-describedby="login-description" tabIndex={-1}>
        <button className="login-dialog__close" type="button" onClick={requestClose} aria-label="Close sign-in dialog" title="Close">×</button>
        <div className="login-dialog__brand"><span className="login-dialog__mark" aria-hidden="true" />GeoGround</div>
        <p className="login-dialog__eyebrow">GEOSPATIAL INTELLIGENCE</p>
        <h2 id="login-title">Welcome to GeoGround</h2>
        <p id="login-description" className="login-dialog__description">Sign in to access your geospatial intelligence workspace.</p>
        <div className="login-preview-notice" role="status">Sign-in is unavailable in this preview.</div>
        <form className="login-form" onSubmit={handleSubmit} noValidate>
          <div className="login-field"><label htmlFor="login-email">Email address</label><input ref={emailRef} id="login-email" type="email" autoComplete="username" placeholder="name@company.com" value={email} onChange={(event) => { setEmail(event.target.value); setErrors((current) => ({ ...current, email: '' })); }} aria-invalid={Boolean(errors.email)} aria-describedby={errors.email ? 'login-email-error' : undefined} />{errors.email && <span className="login-field__error" id="login-email-error">{errors.email}</span>}</div>
          <div className="login-field"><label htmlFor="login-password">Password</label><div className="login-password-wrap"><input ref={passwordRef} id="login-password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Enter your password" value={password} onChange={(event) => { setPassword(event.target.value); setErrors((current) => ({ ...current, password: '' })); }} aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? 'login-password-error' : undefined} /><button type="button" className="login-password-toggle" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? 'Hide password' : 'Show password'} title={showPassword ? 'Hide password' : 'Show password'}><EyeIcon hidden={showPassword} /></button></div>{errors.password && <span className="login-field__error" id="login-password-error">{errors.password}</span>}</div>
          <label className="login-remember"><input type="checkbox" checked={rememberMe} onChange={(event) => setRememberMe(event.target.checked)} disabled aria-describedby="remember-unavailable" /><span>Remember me</span><small id="remember-unavailable">Not available yet</small></label>
          <button className="login-submit" type="submit">Sign In</button>
          {notice && <p className="login-form__notice" role="alert">{notice}</p>}
        </form>
        <div className="login-dialog__links"><a href="#forgot-password" onClick={(event) => { event.preventDefault(); setNotice('Password recovery is not available yet.'); }}>Forgot password?</a><a href="#create-account" onClick={(event) => { event.preventDefault(); setNotice('Account registration is not available yet.'); }}>Create account</a></div>
      </section>
    </div>
  );
}
