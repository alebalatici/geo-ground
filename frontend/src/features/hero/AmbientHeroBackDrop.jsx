import { useEffect, useRef } from 'react';
import { buildTopographicContours } from '../../utils/heroArtGeometry.js';

const VIEWBOX_WIDTH = 1200;
const VIEWBOX_HEIGHT = 400;
const FOLLOW_EASING = 0.12; // 0 = never moves, 1 = jumps instantly
const SETTLE_DISTANCE_PX = 0.4;
const IDLE_POSITION = { x: 0.72, y: 0.38 }; // spotlight rest position (fraction of the hero)

const ORBIT_CENTER = { x: 760, y: 210 };

const FAR_ORBITS = [
  { rx: 620, ry: 170, rotate: -16, dashed: false },
  { rx: 470, ry: 120, rotate: -16, dashed: true, dotAngle: 2.3 },
];

const NEAR_ORBITS = [
  { rx: 540, ry: 140, rotate: -16, dashed: true },
  { rx: 360, ry: 92, rotate: -16, dashed: false, dotAngle: 0.7 },
  { rx: 240, ry: 58, rotate: -16, dashed: true, dotAngle: 4.1 },
];

const CONTOUR_PATHS = buildTopographicContours({
  centerX: 720,
  centerY: 210,
  ringCount: 11,
  startRadius: 46,
  radiusStep: 30,
});

function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum);
}

function BackdropSvg({ children }) {
  return (
    <svg
      className="hero-backdrop__svg"
      viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
      preserveAspectRatio="xMidYMid slice"
      focusable="false"
    >
      {children}
    </svg>
  );
}

function TopographicLayer({ variantClassName }) {
  return (
    <div className={`hero-backdrop__topo ${variantClassName}`}>
      <div className="hero-backdrop__layer hero-backdrop__layer--topo">
        <BackdropSvg>
          {CONTOUR_PATHS.map((pathData) => (
            <path key={pathData} d={pathData} className="hero-backdrop__contour" />
          ))}
        </BackdropSvg>
      </div>
    </div>
  );
}

function OrbitLayer({ orbits, layerClassName }) {
  return (
    <div className={`hero-backdrop__layer ${layerClassName}`}>
      <BackdropSvg>
        {orbits.map((orbit) => (
          <g
            key={`${orbit.rx}-${orbit.ry}`}
            transform={`rotate(${orbit.rotate} ${ORBIT_CENTER.x} ${ORBIT_CENTER.y})`}
          >
            <ellipse
              cx={ORBIT_CENTER.x}
              cy={ORBIT_CENTER.y}
              rx={orbit.rx}
              ry={orbit.ry}
              className={`hero-backdrop__orbit${
                orbit.dashed ? ' hero-backdrop__orbit--dashed' : ''
              }`}
            />
            {orbit.dotAngle !== undefined && (
              <circle
                cx={ORBIT_CENTER.x + orbit.rx * Math.cos(orbit.dotAngle)}
                cy={ORBIT_CENTER.y + orbit.ry * Math.sin(orbit.dotAngle)}
                r="3.5"
                className="hero-backdrop__dot"
              />
            )}
          </g>
        ))}
      </BackdropSvg>
    </div>
  );
}

export default function AmbientHeroBackdrop() {
  const rootRef = useRef(null);

  useEffect(() => {
    const rootElement = rootRef.current;
    const hostElement = rootElement?.parentElement;
    if (!rootElement || !hostElement) return undefined;

    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (reducedMotionQuery.matches) return undefined;

    let hostRect = hostElement.getBoundingClientRect();
    const target = {
      x: hostRect.width * IDLE_POSITION.x,
      y: hostRect.height * IDLE_POSITION.y,
    };
    const current = { ...target };
    let frameId = 0;

    function writeVariables() {
      rootElement.style.setProperty('--mouse-x', `${current.x.toFixed(1)}px`);
      rootElement.style.setProperty('--mouse-y', `${current.y.toFixed(1)}px`);
      // Parallax values go from -1 (left/top edge) to 1 (right/bottom edge).
      rootElement.style.setProperty(
        '--parallax-x',
        ((current.x / hostRect.width - 0.5) * 2).toFixed(4),
      );
      rootElement.style.setProperty(
        '--parallax-y',
        ((current.y / hostRect.height - 0.5) * 2).toFixed(4),
      );
    }

    function tick() {
      const deltaX = target.x - current.x;
      const deltaY = target.y - current.y;
      current.x += deltaX * FOLLOW_EASING;
      current.y += deltaY * FOLLOW_EASING;
      writeVariables();

      const isSettled =
        Math.abs(deltaX) < SETTLE_DISTANCE_PX && Math.abs(deltaY) < SETTLE_DISTANCE_PX;
      frameId = isSettled ? 0 : requestAnimationFrame(tick);
    }

    function scheduleFrame() {
      if (!frameId) frameId = requestAnimationFrame(tick);
    }

    function handlePointerMove(event) {
      hostRect = hostElement.getBoundingClientRect();
      target.x = clamp(event.clientX - hostRect.left, 0, hostRect.width);
      target.y = clamp(event.clientY - hostRect.top, 0, hostRect.height);
      scheduleFrame();
    }

    function handlePointerLeave() {
      hostRect = hostElement.getBoundingClientRect();
      target.x = hostRect.width * IDLE_POSITION.x;
      target.y = hostRect.height * IDLE_POSITION.y;
      scheduleFrame();
    }

    writeVariables();
    hostElement.addEventListener('pointermove', handlePointerMove, { passive: true });
    hostElement.addEventListener('pointerleave', handlePointerLeave);

    return () => {
      hostElement.removeEventListener('pointermove', handlePointerMove);
      hostElement.removeEventListener('pointerleave', handlePointerLeave);
      if (frameId) cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <div ref={rootRef} className="hero-backdrop" aria-hidden="true">
      <div className="hero-backdrop__spotlight" />
      <TopographicLayer variantClassName="hero-backdrop__topo--base" />
      <TopographicLayer variantClassName="hero-backdrop__topo--highlight" />
      <OrbitLayer orbits={FAR_ORBITS} layerClassName="hero-backdrop__layer--orbits-far" />
      <OrbitLayer orbits={NEAR_ORBITS} layerClassName="hero-backdrop__layer--orbits-near" />
    </div>
  );
}