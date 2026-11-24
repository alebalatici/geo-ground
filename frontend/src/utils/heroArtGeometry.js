const FULL_TURN = Math.PI * 2;

function formatNumber(value) {
  return value.toFixed(1);
}

/** Turns a closed list of points into a smooth SVG path (Catmull-Rom to Bezier). */
function buildClosedSmoothPath(points) {
  const count = points.length;
  let pathData = `M ${formatNumber(points[0][0])} ${formatNumber(points[0][1])}`;

  for (let index = 0; index < count; index += 1) {
    const previous = points[(index - 1 + count) % count];
    const current = points[index];
    const next = points[(index + 1) % count];
    const afterNext = points[(index + 2) % count];

    const controlOneX = current[0] + (next[0] - previous[0]) / 6;
    const controlOneY = current[1] + (next[1] - previous[1]) / 6;
    const controlTwoX = next[0] - (afterNext[0] - current[0]) / 6;
    const controlTwoY = next[1] - (afterNext[1] - current[1]) / 6;

    pathData +=
      ` C ${formatNumber(controlOneX)} ${formatNumber(controlOneY)}` +
      ` ${formatNumber(controlTwoX)} ${formatNumber(controlTwoY)}` +
      ` ${formatNumber(next[0])} ${formatNumber(next[1])}`;
  }

  return `${pathData} Z`;
}

/** One organic, slightly irregular closed contour line. */
export function buildContourPath({
  centerX,
  centerY,
  radius,
  wobble,
  phase,
  horizontalStretch,
  verticalSquash,
  pointCount = 56,
}) {
  const points = [];
  for (let index = 0; index < pointCount; index += 1) {
    const angle = (index / pointCount) * FULL_TURN;
    const noise =
      Math.sin(angle * 2 + phase) * 0.5 +
      Math.sin(angle * 3 - phase * 1.7) * 0.3 +
      Math.sin(angle * 5 + phase * 0.6) * 0.2;
    const ringRadius = radius * (1 + wobble * noise);
    points.push([
      centerX + Math.cos(angle) * ringRadius * horizontalStretch,
      centerY + Math.sin(angle) * ringRadius * verticalSquash,
    ]);
  }
  return buildClosedSmoothPath(points);
}

/** A set of nested contour lines, like the height lines of a topographic map. */
export function buildTopographicContours({
  centerX,
  centerY,
  ringCount,
  startRadius,
  radiusStep,
  horizontalStretch = 1.45,
  verticalSquash = 0.78,
}) {
  return Array.from({ length: ringCount }, (_, ringIndex) =>
    buildContourPath({
      centerX,
      centerY,
      radius: startRadius + ringIndex * radiusStep,
      wobble: 0.05 + ringIndex * 0.012,
      phase: ringIndex * 0.38,
      horizontalStretch,
      verticalSquash,
    }),
  );
}