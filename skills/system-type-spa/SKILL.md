---
name: system-type-spa
description: "Domain patterns for single-page application architecture — client-side routing, state management, rendering strategies, authentication, performance, and offline support. Use when designing or evaluating a browser-based SPA, progressive web app, or rich client-side application."
---

# System Type: Single-Page Application (SPA)

Patterns, failure modes, and anti-patterns for browser-based single-page applications.

---

## Rendering Strategies

### Client-Side Rendering (CSR)
**When to use.** Interactive applications where SEO is not critical — dashboards, admin panels, internal tools, authenticated experiences. When the team already has frontend expertise and the app's value is in interactivity, not content discovery.
**When to avoid.** Content-heavy marketing sites, blogs, e-commerce product pages — anything where first meaningful paint and SEO matter. When users are on slow devices or unreliable networks.
**Key decisions.** Shell loading strategy (skeleton screens vs spinners), code splitting granularity, initial bundle size budget, CDN caching for static assets.

### Server-Side Rendering (SSR)
**When to use.** When first contentful paint matters for conversion. Public-facing pages that need SEO. When you need the interactivity of a SPA but can't sacrifice initial load performance.
**When to avoid.** Purely authenticated apps where crawlers never see content. When the backend team can't support a Node.js rendering tier. When the added infrastructure complexity isn't justified by the SEO/performance benefit.
**Key decisions.** Hydration strategy (full hydration, partial, progressive, islands), streaming vs buffered SSR, caching rendered HTML, handling authentication during SSR, server cost for rendering.

### Static Site Generation (SSG)
**When to use.** Content that changes infrequently — documentation, marketing pages, blogs. When you want SPA-like navigation but with pre-built HTML for instant loads.
**When to avoid.** Highly dynamic, personalized content. Pages that change per-user or per-request. Large sites with millions of pages where build times become prohibitive.
**Key decisions.** Build frequency, incremental regeneration strategy, preview/draft workflow, handling dynamic sections within static pages.

### Islands Architecture
**When to use.** Mostly-static pages with isolated interactive widgets. When you want to ship minimal JavaScript and hydrate only the components that need interactivity.
**When to avoid.** Heavily interactive applications where most of the page is dynamic. When shared state between islands creates coupling that negates the isolation benefit.
**Key decisions.** Island boundary identification, shared state between islands, framework choice (Astro, Fresh, 11ty), progressive enhancement baseline.

## Client-Side Routing

### Hash-Based Routing
**When to use.** Legacy browser support. Deployments where you can't configure server-side fallback routes (e.g., static file hosting without URL rewriting). Simple applications that don't need clean URLs.
**When to avoid.** Any modern application where clean URLs matter. When anchor links are needed for in-page navigation.
**Key decisions.** None significant — this is a fallback strategy, not a primary choice.

### History API Routing
**When to use.** The default for modern SPAs. Clean URLs, proper browser back/forward behavior, shareable deep links.
**When to avoid.** Environments where the server can't be configured to serve the SPA shell for all routes (static hosting without rewrite rules). In those cases, hash routing or SSG is better.
**Key decisions.** Server fallback configuration (all unmatched routes serve index.html), route-based code splitting, scroll restoration, route transition animations, route guards for authentication.

### Route-Based Code Splitting
**When to use.** Any SPA beyond trivial size. Load code for a route only when the user navigates to it. Essential for keeping initial bundle size manageable.
**When to avoid.** Extremely small applications where the overhead of chunking exceeds the benefit.
**Key decisions.** Chunk granularity (per route, per feature, per library), preloading strategy for likely next routes, loading state during chunk fetch, handling chunk load failures (version mismatch after deployment).

## State Management

### Local Component State
**When to use.** UI state that belongs to a single component — form inputs, toggles, dropdown open/closed, animation state. The default; reach for shared state only when local state creates prop drilling pain.
**When to avoid.** State that multiple unrelated components need. State that must survive component unmounting.
**Key decisions.** When to lift state vs. when to share it. Keeping state as close to where it's used as possible.

### Global State (Redux, Zustand, Jotai, Signals)
**When to use.** State shared across many components — user session, feature flags, shopping cart, notification queue. State that must be inspectable and debuggable (Redux DevTools). State with complex update logic that benefits from centralization.
**When to avoid.** Simple applications where React context or component state suffices. Using global state as a default rather than an escalation — this is the most common state management mistake.
**Key decisions.** Store shape (normalized vs nested), selector granularity (over-subscribing causes re-renders), middleware for side effects, persistence strategy, hydration from SSR.

### Server State (React Query, SWR, Apollo)
**When to use.** Any data that comes from a server and may be stale. These libraries handle caching, revalidation, deduplication, and background refresh — problems you will solve badly if you solve them manually.
**When to avoid.** Purely local state. Offline-first applications where the server is not the source of truth.
**Key decisions.** Cache invalidation strategy, stale-while-revalidate timing, optimistic updates, error retry policy, query key design (determines cache boundaries), prefetching strategy.

### URL State
**When to use.** Filter selections, search queries, pagination, sort order — anything the user should be able to bookmark or share via URL. Often overlooked as a state management tool.
**When to avoid.** Sensitive data. High-frequency updates (every keystroke). State that doesn't make sense to share or bookmark.
**Key decisions.** Serialization format (query params vs path segments), default value handling, URL length limits, backward compatibility when URL schema changes.

## Authentication Patterns

### Token-Based (JWT)
**When to use.** SPAs that call APIs on a different domain. When the backend is stateless. When you need to include claims (roles, permissions) in the token to reduce backend lookups.
**When to avoid.** When you can use HTTP-only cookies instead (same-domain APIs) — cookies are harder to steal via XSS. When token revocation is a hard requirement (JWTs are valid until expiry).
**Key decisions.** Storage location (memory vs localStorage — memory is safer, localStorage survives refresh), refresh token rotation, token expiry duration, silent refresh mechanism, logout propagation across tabs.

### HTTP-Only Cookie
**When to use.** When the API is on the same domain (or a subdomain). The most secure browser storage mechanism — not accessible to JavaScript, eliminating the XSS token theft vector.
**When to avoid.** Cross-origin API calls where cookies can't be sent. Mobile app backends where cookies are awkward.
**Key decisions.** SameSite attribute (Strict vs Lax), CSRF protection (double-submit cookie or synchronizer token), cookie scope (domain, path), secure flag enforcement.

### OAuth / OIDC Flows
**When to use.** Third-party login (Google, GitHub, Microsoft). Enterprise SSO. When you don't want to manage passwords.
**When to avoid.** Simple applications with only email/password auth where the OAuth complexity isn't justified.
**Key decisions.** Authorization Code flow with PKCE (required for SPAs — implicit flow is deprecated), redirect vs popup, state parameter for CSRF, token storage after callback, session management across tabs.

## Performance

### Bundle Size
**What it costs.** Every kilobyte of JavaScript must be downloaded, parsed, and executed. On a mid-range mobile device, 1 MB of JavaScript can take 3-4 seconds to parse alone. Bundle size is the single largest performance lever for SPAs.
**Key strategies.** Tree shaking (ensure ESM imports), code splitting by route and feature, dynamic imports for heavy libraries, bundle analysis (webpack-bundle-analyzer, source-map-explorer), size budgets enforced in CI, replacing heavy libraries with lighter alternatives.

### Rendering Performance
**What it costs.** Unnecessary re-renders cause jank, input lag, and battery drain. React's reconciliation is fast but not free — large component trees with frequent updates are the primary source of SPA sluggishness.
**Key strategies.** Memoization (React.memo, useMemo, useCallback — but measure first), virtualized lists for large datasets, debounced inputs, avoiding state updates that trigger full tree re-renders, profiler-guided optimization (React DevTools Profiler, Chrome Performance tab).

### Network Performance
**What it costs.** API waterfalls — sequential requests where one fetch depends on another — are the most common cause of slow SPA page loads. Users perceive network-bound delays as the app being slow.
**Key strategies.** Parallel data fetching, request deduplication, prefetching on hover/focus, cache-first patterns for stable data, skeleton screens that match actual layout, avoiding layout shift during load.

### Core Web Vitals
**What it costs.** LCP (Largest Contentful Paint), INP (Interaction to Next Paint), and CLS (Cumulative Layout Shift) directly affect search ranking and user perception. SPAs historically struggle with all three.
**Key strategies.** Preload critical resources, inline critical CSS, reserve space for dynamic content (prevents CLS), break long tasks to keep main thread responsive (improves INP), use loading="lazy" for below-fold images.

## Offline and PWA

### Service Workers
**When to use.** Offline support, background sync, push notifications, asset precaching. Any SPA that should work (even partially) without a network connection.
**When to avoid.** Applications where stale data is dangerous (financial dashboards, real-time monitoring). When the team doesn't understand service worker lifecycle — a broken service worker can cache bad code with no recovery path for users.
**Key decisions.** Caching strategy per resource type (cache-first for assets, network-first for API), cache versioning and cleanup, update notification to users ("new version available"), scope management, handling service worker update when tabs are open.

### Offline Data
**When to use.** Applications used in unreliable network conditions — field work, mobile, transit. Forms that should not lose data on disconnection.
**When to avoid.** When the conflict resolution complexity exceeds the offline benefit. When data freshness is critical and stale data causes harm.
**Key decisions.** Local storage technology (IndexedDB for structured data, localStorage for simple key-value), sync strategy (background sync API, manual queue), conflict resolution on reconnection, storage quota management, user communication about offline state.

## Common Failure Modes

- **Stale deployment cache.** Users load cached JavaScript bundles that reference API contracts or chunk filenames that no longer exist. Mitigation: content-hashed filenames, versioned API endpoints, chunk load error handling that forces a page refresh.
- **Memory leaks from event listeners and subscriptions.** Components mount listeners or subscriptions and never clean them up. Over time, the tab consumes gigabytes. Mitigation: cleanup in useEffect return / componentWillUnmount, WeakRef where appropriate, monitoring tab memory in production.
- **White screen of death.** An unhandled JavaScript error crashes the entire component tree. Mitigation: error boundaries at route and feature level, fallback UI, error reporting to monitoring service.
- **State desynchronization.** Client state diverges from server state — the user sees stale data, makes decisions on wrong information, or submits conflicting updates. Mitigation: server state as source of truth (React Query/SWR), optimistic update rollback on failure, staleness indicators.
- **Infinite loading states.** A failed network request with no timeout or error handling leaves the user staring at a spinner forever. Mitigation: request timeouts, error states with retry, circuit breaker for known-failing endpoints.
- **Route-level code split failures.** After a deployment, users on old cached pages try to navigate to a route whose chunk filename has changed. The dynamic import fails silently. Mitigation: chunk error detection, automatic page reload on chunk load failure, service worker precaching of route chunks.
- **Authentication token expiry during use.** The user is mid-workflow when their token expires. The next API call fails, and unsaved work is lost. Mitigation: silent token refresh before expiry, queuing requests during refresh, saving form state to localStorage as backup.
- **Hydration mismatch.** SSR HTML doesn't match what the client renders, causing React to discard the server-rendered DOM and re-render from scratch — negating the SSR performance benefit. Mitigation: ensure server and client render identical output, suppress hydration warnings only as last resort, avoid browser-only APIs during SSR (window, localStorage).

## Anti-Patterns

- **Mega-bundle.** Shipping the entire application as a single JavaScript file. Users download megabytes of code they won't use on the current page. Split by route at minimum.
- **Global state for everything.** Putting form input state, UI toggles, and animation state into Redux/Zustand. Global state is for shared, cross-cutting concerns — not a replacement for component state.
- **Prop drilling avoidance via global state.** Reaching for a global store because props pass through 3 components. Composition (children, render props, context) solves this without the overhead.
- **Direct DOM manipulation.** Using querySelector or innerHTML alongside a virtual DOM framework. The framework can't track changes it didn't make, leading to subtle rendering bugs.
- **Client-side security.** Hiding UI elements instead of enforcing permissions on the API. Every API endpoint must validate authorization independently — the client is untrusted.
- **Storing secrets in JavaScript.** API keys, service credentials, or admin tokens in client-side code. JavaScript source is fully visible to users. Use a backend proxy for authenticated third-party calls.
- **SPA for content sites.** Building a blog, documentation site, or marketing page as a CSR SPA. These need SEO, fast first paint, and work without JavaScript. Use SSG or SSR.
- **Ignoring accessibility.** SPAs break native browser accessibility by default — no page load announcements, focus management on route change, or semantic HTML. Accessibility must be designed in, not retrofitted.
- **No loading or error states.** Assuming every API call succeeds instantly. Every async operation needs three states: loading, success, error. Skipping any of these guarantees a bad user experience.
- **Over-abstracting too early.** Creating a generic DataFetcher, FormBuilder, or LayoutEngine before understanding the actual use cases. Premature abstraction in frontend code creates rigid, hard-to-debug component hierarchies.
