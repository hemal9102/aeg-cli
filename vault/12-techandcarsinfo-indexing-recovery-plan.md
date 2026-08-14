# TechAndCarsInfo Indexing Recovery Plan

**Created:** 2026-08-13  
**Domain:** `https://techandcarsinfo.com`  
**Goal:** Move from "crawlable but mostly unindexed" to stable index growth.

---

## 1. Executive Diagnosis

This is **not** a hard crawl blocking incident. The site is reachable, crawlable, and serving 200 for key URLs.  
The main failure is **index selection** (Google chooses not to index most URLs yet), likely due to:

1. Discovery/canonical hygiene gaps (`/sitemap.xml` missing, host canonicalization not enforced via redirect).
2. Low trust/quality selection signals across many URLs published in a similar time window.
3. Insufficient authority for broad-scale URL acceptance.

---

## 2. Evidence Snapshot (from audit)

1. `robots.txt` is 200 and allows `/` (public crawl is open).
2. Main pages and sampled posts return 200 with canonical tags.
3. `sitemap-blog.xml` is live with ~47 URLs.
4. `sitemap.xml` returns 404 (should be valid and submitted).
5. `www` host serves 200; canonical points to non-www, but no hard `301 www -> non-www`.
6. GSC export: 47 URLs tracked, 46 not indexed/invisible.

---

## 3. Recovery Strategy (Phased)

## Phase 0 - Baseline and Measurement (Day 0)

**Outcome:** You can measure impact of every fix.

1. In GSC, keep only one primary property for analysis (domain property preferred).
2. Export current coverage by reason:
   - Unknown to Google
   - Crawled currently not indexed
   - Discovered currently not indexed
3. Freeze baseline metrics:
   - Indexed URL count
   - Valid impressions/clicks (last 28 days)
   - Crawl stats requests/day
4. Keep a weekly scorecard in this file (append section at bottom).

---

## Phase 1 - Critical Technical Fixes (Day 1-2)

**Outcome:** Remove avoidable technical ambiguity.

### A. Fix Sitemap Endpoint Contract
1. Make `/sitemap.xml` return 200.
2. Prefer sitemap index format:
   - `/sitemap.xml` -> references `/sitemap-blog.xml`
3. Keep both URLs live:
   - `/sitemap.xml` (index entrypoint)
   - `/sitemap-blog.xml` (URL set)
4. Re-submit `/sitemap.xml` in GSC.

### B. Enforce Single Canonical Host + Protocol
1. Enforce redirect chain:
   - `http://techandcarsinfo.com/*` -> `https://techandcarsinfo.com/*` (301)
   - `http://www.techandcarsinfo.com/*` -> `https://techandcarsinfo.com/*` (301)
   - `https://www.techandcarsinfo.com/*` -> `https://techandcarsinfo.com/*` (301)
2. Ensure exactly one hop, no 302.

### C. Keep Robots Simple and Stable
1. Ensure `robots.txt` includes:
   - `User-agent: *`
   - `Allow: /`
   - limited disallow for private areas only
   - `Sitemap: https://techandcarsinfo.com/sitemap.xml`
2. Avoid over-complex bot-specific blocks during recovery.

### D. Verify Canonical/Status Matrix
For homepage, blog index, 10 priority posts:
1. Status = 200
2. Canonical = self URL on canonical host
3. No `noindex` in HTML/meta/header
4. Internal links point directly to canonical URLs

---

## Phase 2 - Indexability Prioritization (Day 3-7)

**Outcome:** Ask Google to index only strongest assets first.

### A. Tier URLs by quality
1. **Tier 1 (10-15 URLs):** best content depth, clear intent, strongest titles/slugs.
2. **Tier 2 (next 15-20 URLs):** medium quality pages.
3. **Tier 3:** weak/generic/placeholder-like pages.

### B. Quality Controls Before Indexing Requests
Each Tier 1 page must pass:
1. Unique and specific title/H1.
2. Strong intro answering query intent in first 100 words.
3. Original data/examples/comparison table where relevant.
4. 3-5 contextual internal links from and to related pages.
5. Clean FAQ section only if truly useful.

### C. Handle weak URLs
1. Improve or merge thin/overlapping pages.
2. If page has no clear unique value, set `noindex, follow` temporarily.
3. Remove obvious junk-intent slugs from active index push queue until rewritten.

---

## Phase 3 - Authority and Crawl Demand (Week 2-4)

**Outcome:** Improve selection probability for remaining URLs.

1. Build 5-10 real backlinks to Tier 1 pages (editorial mentions, niche communities, partner citations).
2. Publish 2 high-trust support assets:
   - Original research-style post (data-led)
   - High-quality comparison guide
3. Strengthen entity signals:
   - Consistent Organization schema
   - Author bylines with credentials
   - Updated About/Editorial policy pages
4. Maintain publication cadence (avoid mass low-differentiation drops).

---

## 4. GSC Submission Protocol

1. Submit/update sitemap once technical fixes are live.
2. Request indexing only for Tier 1 URLs first (10-15 max per batch).
3. Wait 7-10 days, review status changes.
4. If acceptance improves, move to Tier 2.
5. Do not repeatedly re-request low-quality URLs without substantial content updates.

---

## 5. File-Level Implementation Map (TechAndCarsInfo codebase)

1. **Routing/redirects:** `.htaccess` and `router.php`
   - Add/enforce `www -> non-www` + `http -> https` behavior
2. **Sitemap routing:** `.htaccess`, `router.php`, `sitemap.php` / `sitemap-xml.php`
   - Ensure `/sitemap.xml` is valid and canonical
3. **Robots output:** `controllers/Site/StaticPageController.php` (`robots()`)
   - Point sitemap line to `/sitemap.xml`
4. **Meta/canonical consistency:** `site/lib/seo.php`
   - Keep canonical generation stable and host-consistent

Note: if you change routes in this project, keep `.htaccess` and `router.php` synchronized.

---

## 6. Validation Checklist (Must Pass)

1. `/robots.txt` = 200 and includes `Sitemap: https://techandcarsinfo.com/sitemap.xml`
2. `/sitemap.xml` = 200 and parseable XML
3. `/sitemap-blog.xml` = 200 and expected URL count
4. `www/http` variants = single-hop 301 to `https://techandcarsinfo.com/...`
5. Priority URLs: 200 + self canonical + no noindex
6. GSC: first Tier 1 URLs transition from unknown/not indexed to indexed over 2-4 weeks

---

## 7. 30-Day Success Criteria

1. Index coverage: 46 non-indexed -> <= 20 non-indexed.
2. Tier 1 acceptance: >= 60% indexed.
3. Impressions trend: positive week-over-week on indexed pages.
4. Crawl stats: stable or increasing fetches without error spikes.

---

## 8. Weekly Tracking Template

Copy and append weekly:

```md
### Week YYYY-MM-DD
- Indexed URLs:
- Non-indexed URLs:
- Tier 1 indexed / total:
- New impressions:
- New clicks:
- Technical blockers found:
- Actions completed:
- Next week focus:
```

