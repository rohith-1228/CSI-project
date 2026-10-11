import '@testing-library/jest-dom/vitest';

// Polyfill scrollIntoView for jsdom
if (typeof window !== 'undefined') {
  window.HTMLElement.prototype.scrollIntoView = () => {};
}
