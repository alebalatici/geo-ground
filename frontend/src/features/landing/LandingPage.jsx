import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import HeroSection from '../hero/HeroSection.jsx';
import TopNavbar from '../header/TopNavbar.jsx';
import './landing.css';

const ENTERPRISE_PRICE = import.meta.env.VITE_ENTERPRISE_PRICE || '€49';

const plans = [
  {
    name: 'Executive',
    audience: 'For investors, agents, and decision-makers tracking property opportunities.',
    price: 'Free',
    summary: 'Monitor sites, review satellite signals, and get a concise AI brief.',
    available: ['Interactive satellite map', 'Site monitoring and available alerts', 'Year selector and historical context', 'AI executive brief and site assistant'],
    action: 'Explore Executive',
    to: '/executive',
  },
  {
    name: 'Enterprise',
    audience: 'For GIS specialists, analysts, and real estate teams working at scale.',
    price: ENTERPRISE_PRICE,
    cadence: '/ month',
    summary: 'An early look at advanced geospatial intelligence for professional teams.',
    planned: ['Advanced satellite telemetry and analytics', 'NDVI and SAR analysis workflows', 'Detailed change detection and monitoring', 'Advanced AI intelligence features'],
    action: 'Explore Enterprise Demo',
    to: '/enterprise',
    featured: true,
  },
];

function PlanIcon({ enterprise }) {
  return enterprise ? (
    <svg viewBox="0 0 32 32" width="25" height="25" fill="none" aria-hidden="true"><circle cx="16" cy="16" r="10" stroke="currentColor" strokeWidth="1.5"/><ellipse cx="16" cy="16" rx="14" ry="5.5" transform="rotate(-28 16 16)" stroke="currentColor" strokeWidth="1.5"/><circle cx="26" cy="10" r="2.3" fill="currentColor"/></svg>
  ) : (
    <svg viewBox="0 0 32 32" width="25" height="25" fill="none" aria-hidden="true"><path d="M5 24.5 12.2 17l4.6 4.6L27 10.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path d="M20 10.5h7v7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><circle cx="8" cy="10" r="3" stroke="currentColor" strokeWidth="1.5"/><circle cx="8" cy="10" r=".8" fill="currentColor"/></svg>
  );
}

function PlanCard({ plan }) {
  return <article className={`plan-card${plan.featured ? ' plan-card--featured' : ''}`}>
    <div className="plan-card__top"><div className="plan-card__identity"><span className="plan-card__icon"><PlanIcon enterprise={plan.featured} /></span><div><p className="plan-card__eyebrow">{plan.featured ? 'Early preview' : 'For confident decisions'}</p><h3>{plan.name}</h3></div></div>{plan.featured && <span className="plan-card__badge">PREVIEW</span>}</div>
    <p className="plan-card__audience">{plan.audience}</p>
    <p className="plan-card__price"><strong>{plan.price}</strong>{plan.cadence && <span>{plan.cadence}</span>}</p>
    {plan.featured && <p className="plan-card__note">Indicative pricing · capabilities in development</p>}
    <p className="plan-card__summary">{plan.summary}</p>
    <h4>{plan.featured ? 'Planned for Enterprise' : 'Included'}</h4>
    <ul>{(plan.available || plan.planned).map((item) => <li key={item}><span aria-hidden="true">{plan.featured ? '○' : '✓'}</span>{item}</li>)}</ul>
    <Link className={`plan-card__action${plan.featured ? ' plan-card__action--secondary' : ''}`} to={plan.to}>{plan.action}<span aria-hidden="true">→</span></Link>
  </article>;
}

export default function LandingPage({ onSignIn }) {
  useEffect(() => {
    if (!window.location.hash) return;
    const target = document.getElementById(window.location.hash.slice(1));
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, []);
  return <div className="landing-page"><TopNavbar variant="landing" onSignIn={onSignIn} /><HeroSection primaryLabel="Explore Plans" primaryTargetId="plans" />
    <main>
      <section id="plans" className="landing-plans" aria-labelledby="plans-title"><div id="platform" className="landing-section-heading"><p className="landing-kicker">Choose your perspective</p><h2 id="plans-title">Ground your next decision in better intelligence.</h2><p>Explore practical site monitoring today and see what is planned for professional teams.</p></div><div className="plan-grid">{plans.map((plan) => <PlanCard key={plan.name} plan={plan} />)}</div></section>
      <section id="mission" className="landing-mission"><div><p className="landing-kicker">Our Mission</p><h2>Make the ground story visible.</h2></div><p>GeoGround helps real estate professionals understand how land and properties change over time by bringing satellite observations and site intelligence into one place.</p></section>
    </main>
    <footer className="landing-footer"><Link className="landing-brand" to="/"><span className="landing-brand__mark" aria-hidden="true" />GeoGround</Link><span>Satellite intelligence for informed real estate decisions.</span></footer>
  </div>;
}
