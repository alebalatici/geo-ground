import { HERO_CONTENT } from '../../config/appContent.js';
import { scrollToSection } from '../../utils/scrollHelpers.js';
import AmbientHeroBackdrop from './AmbientHeroBackdrop.jsx';
import './hero.css';

function handleSectionClick(event, targetId) {
  if (scrollToSection(targetId)) {
    event.preventDefault();
  }
}

export default function HeroSection() {
  const { eyebrow, title, headline, description, primaryButton, secondaryButton } = HERO_CONTENT;

  return (
    <section className="hero" aria-labelledby="hero-title">
      <AmbientHeroBackdrop />

      <div className="hero__content">
        <p className="hero__eyebrow">{eyebrow}</p>
        <h1 id="hero-title" className="hero__title">
          {title}
        </h1>
        <p className="hero__headline">{headline}</p>
        <p className="hero__description">{description}</p>

        <div className="hero__actions">
          <a
            href={`#${primaryButton.targetId}`}
            className="hero__button hero__button--primary"
            onClick={(event) => handleSectionClick(event, primaryButton.targetId)}
          >
            {primaryButton.label}
          </a>
          <a
            href={`#${secondaryButton.targetId}`}
            className="hero__button hero__button--secondary"
            onClick={(event) => handleSectionClick(event, secondaryButton.targetId)}
          >
            {secondaryButton.label}
          </a>
        </div>
      </div>
    </section>
  );
}