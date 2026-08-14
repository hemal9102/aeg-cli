# SEO & Analytics Architecture (GA4)

## 1. Google Analytics 4 (GA4) Setup
- **Property ID:** `541897723`
- **Data Collection Strategy:** Shifted from basic traffic reporting to predictive analytics and technical health monitoring.
- **MCP Integration:** GA4 MCP is connected via Service Account (`automation-api@cosmic-mariner-503804-c4.iam.gserviceaccount.com`) with Viewer access to run internal Python reporting scripts.

## 2. Advanced Tracking Events
The following custom events must be pushed to the GA4 dataLayer:
- `core_web_vitals`: Tracking LCP, CLS, INP directly in GA4 to monitor codebase bloat.
- `js_error`: Custom event to track 404s and client-side routing bugs on dynamic pages.
- `file_upload`: Triggered when a candidate successfully uploads a CV (used for Closed Funnel exploration).
- `view_search_results`: To identify zero-result search queries and build new landing pages based on demand.

## 3. SEO Architecture & Clean Routing
- **URL Structure:** Moving away from static `.html` extensions. Transitioning to clean, modular routes (e.g., `/recruitment-agency-in-ahmedabad`) to support scale.
- **Canonical Tags:** Implementing strict canonical tags on all dynamic and city-hub pages to prevent duplicate content indexation by Googlebot.
- **Structured Data:** Mandatory JSON-LD Schema implementation in the `<head>`:
  - `EmploymentAgency` schema for brand and local relevance.
  - `JobPosting` schema for individual job vacancies to qualify for the Google Jobs snippet (Blue Box).

## 4. Multi-City Expansion Strategy (Programmatic)
- Focus on high-intent city hubs (Ahmedabad, Mumbai, Vadodara, Rajkot).
- **GMB Tracking:** Google Business Profile links must include UTM parameters (`?utm_source=google&utm_medium=organic&utm_campaign=gbp_listing`) to isolate local listing traffic from general organic search.
- **IndexNow:** Planned implementation of the IndexNow protocol to instantly ping search engines when a new job is posted.

## 5. Automation Future-Proofing
- **Server-Side GTM (sGTM):** Planned migration to bypass ad-blockers and improve client-side performance.
- **GMB MCP:** Planned OAuth 2.0 implementation to allow the agent to manage Google Business Profiles automatically (reply to reviews, post updates).

## 6. GA4 Current Data Baseline & Insights
- **Scroll Tracking:** Active. 45% of users scroll (167 out of 365), indicating CTA buttons must be placed above the fold.
- **Internal Search (`view_search_results`):** Currently 0 events. Needs UI enablement in Enhanced Measurement.
- **Conversion Drop-off (`file_upload`):** Currently 0 events (0.0% conversion). Codebase integration is pending for CV upload tracking.

---

## 7. Incident Log: TechAndCarsInfo Indexing Stall (2026-08-13)

### Observed State
- Sitemap crawl health is fine (2xx), but index coverage is near-zero.
- 47 sitemap URLs discovered; 46 are not indexed / invisible in GSC exports.
- Sample status signals include:
  - `URL is unknown to Google`
  - `Crawled - currently not indexed` (not blocked, but not selected)

### Technical Findings
- `robots.txt` is accessible and allows crawl for public pages.
- Canonicals are present and point to `https://techandcarsinfo.com/...`.
- `https://techandcarsinfo.com/sitemap.xml` currently returns 404 while `sitemap-blog.xml` is live.
- `https://www.techandcarsinfo.com/` serves 200 instead of hard 301 to canonical host.

### Primary Diagnosis
- This is not a strict crawl block. It is an index-selection and trust-priority issue amplified by weak discovery hygiene (`/sitemap.xml` missing and host canonicalization not enforced with redirects).

### Recovery Runbook
- See: `vault/12-techandcarsinfo-indexing-recovery-plan.md`
