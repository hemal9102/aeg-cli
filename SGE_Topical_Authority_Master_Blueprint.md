# 🚀 SGE & Topical Authority Master Blueprint (2026)
**Goal:** Transform Jobrecruitment.in from a standard programmatic job board into an **AEO (Answer Engine Optimized)** Topical Authority Hub. The end goal is generating high-quality B2B leads by dominating Google AI Overviews (SGE), ChatGPT, and Perplexity.

---

## 🛡️ 1. Ranking Protection Protocol (Strict GSC & GA4 Validation)
**CRITICAL RISK:** Big-bang deletions of 39,950 pSEO pages can trigger massive ranking drops.

**The Strict Validation Execution (Aug 11, 2026):**
We are using the exact logic from `classify_pseo_pages.py`. A page MUST prove its worth in both Google Search Console (visibility) AND Google Analytics 4 (human engagement) to survive.

**The Threshold & Output (Reconciled to exactly 39,950 pages):**
- **🏆 PILLAR PAGES (1 URL):** Must have `>= 5 GSC Clicks AND >= 3 GA4 Engaged Sessions`. 
  - *Action:* **HTTP 200 (OK)**. We only have 1 true golden pillar that passed this strict test. (Note: We are deliberately keeping this strict threshold. Topical authority will primarily be built through the core whitelist pages: home, jobs, contact, about, employer).
- **🟡 WEAK BUT INDEXED (955 URLs):** Pages that had at least >0 impressions or >0 engaged sessions but failed the strict pillar test.
  - *Action:* **HTTP 301 (Permanent Redirect)**. Mappings have been manually verified in `summary.txt` to avoid silent fallback errors.
- **🔴 DEAD WEIGHT (38,994 URLs):** Absolute zero impressions and zero engagement. 
  - *Action:* **HTTP 410 (Gone)**.

**Batch Rollout Safety:** We will NOT 410 all 38,994 pages on day one. We will roll out the 410s in batches of 5,000-10,000 pages per week while monitoring the GSC Coverage Report to ensure no collateral damage.

---

## 🚨 2. Security & Technical Debt Fixes
**Priority 1: `article.php` Fatal Error & Path Leak**
Google has indexed a page hitting `article.php` which throws a raw PHP fatal error, leaking the physical server path (`/home/u390470426/domains/...`). 
- **Action:** We will enforce `ini_set('display_errors', 0);` in production and wrap the `article.php` logic in a try/catch block that returns a graceful 404 or redirects to the blog index.

**Priority 2: XML Sitemap Pruning**
- **Action:** The XML sitemap generator script will be updated to STRICTLY include only HTTP 200 pages. The 955 Weak and 38,994 Dead pages will be purged from the sitemap to prevent Google from wasting crawl budget on 301s and 410s.

---

## 🏗️ 3. The PSEO Codebase Changes (.htaccess & Caching)
To handle traffic routing securely and performantly.

### Code Implementation (`.htaccess`):
*Updated to ensure extensionless URLs like `/jobs` are also caught if needed, while honoring the whitelist.*
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
# Matches .html or extensionless slugs
RewriteRule ^([a-zA-Z0-9-]+)(?:\.html|/?)$ backend/api/pseo_traffic_controller.php?slug=$1 [L,QSA]
```

### Code Implementation (`pseo_traffic_controller.php` with APCu):
*Updated to use APCu caching so we don't do disk I/O & json_decode on 1,700+ array keys on every single page hit.*
```php
<?php
// Performance: Load from APCu Cache if available, otherwise read disk once
$cacheKey = 'pseo_classification_data';
$trafficData = apcu_fetch($cacheKey);

if ($trafficData === false) {
    $trafficData = json_decode(file_get_contents('report/pseo_classification.json'), true);
    apcu_store($cacheKey, $trafficData, 3600); // Cache for 1 hour
}

$requestSlug = $_GET['slug'] ?? '';
$safeWhitelist = ['home', 'jobs', 'contact', 'about', 'employer'];

if (in_array($requestSlug, $safeWhitelist)) {
    include $requestSlug . '.html';
    exit;
} elseif (in_array($requestSlug, $trafficData['pillar'])) {
    include 'job.php';
    exit;
} elseif (array_key_exists($requestSlug, $trafficData['weak'])) {
    // Verified mapping from Python script
    $targetSlug = $trafficData['weak'][$requestSlug];
    if (empty($targetSlug)) {
        $targetSlug = 'jobs'; // Fallback only if mapping was empty
    }
    header("Location: https://jobrecruitment.in/{$targetSlug}.html", true, 301);
    exit;
} else {
    // Check go_live_date logic for batched 410s here
    header("HTTP/1.1 410 Gone");
    echo "<h1>410 - This job category is no longer available.</h1>";
    exit;
}
?>
```

---

## 🧠 4. The AI Knowledge Graph (llms.txt)
We are feeding Google/OpenAI exact AEO context.

### Code Implementation (To be injected into `llms.php`):
*Schema validated for schema.org compliance (`EmploymentAgency` & `ProfessionalService`).*

```php
echo "### B2B Employer Schema (Corporate Hiring)\\n";
$b2bSchema = [
    "@context" => "https://schema.org",
    "@type" => ["EmploymentAgency", "ProfessionalService"], // Valid schema.org types
    "@id" => "https://jobrecruitment.in/employer.html#b2b",
    "name" => "Job Recruitment - Corporate Hiring Services",
    "founder" => ["@type" => "Person", "name" => "Omear Memon"],
    "description" => "Executive search, bulk hiring, and IT staffing solutions for enterprises in Ahmedabad.",
    "areaServed" => "Ahmedabad, Gujarat, India",
    "url" => "https://jobrecruitment.in/employer.html",
    "telephone" => "+91-9099876985"
];
echo json_encode($b2bSchema, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);

// Massive DB Dump of Active Jobs
echo "### ALL Active JobPosting Schemas (Massive Database Dump)\\n";
$stmt = $pdo->query("SELECT * FROM jobs WHERE deleted_at IS NULL AND status = 'Active'");
while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
    // Generate and echo JobPosting JSON-LD
}
```

---

## 🎯 5. The B2B Lead Generation Engine (GA4 Tracking)
We are fixing the `/employer.html` form. Inline `onsubmit` is fragile, so we are replacing it with a robust JavaScript Event Listener.

1. **Backend Script (`process_b2b_lead.php`):** Saves the POSTed lead securely to `contact_messages`.
2. **GA4 Event Tracking (Robust JS):**
```html
<script>
document.addEventListener("DOMContentLoaded", function() {
    const employerForm = document.getElementById("b2b-lead-form");
    if (employerForm) {
        employerForm.addEventListener("submit", function(e) {
            // Push event safely
            if (typeof gtag === 'function') {
                gtag('event', 'generate_lead', {
                    'event_category': 'B2B',
                    'event_label': 'Employer Form'
                });
            }
        });
    }
});
</script>
```

---

## 🗣️ 6. The 100 FAQs SGE Injection Strategy
*Guideline: Avoid FAQPage schema stuffing. Every FAQ must be a genuine, visible Q&A on the page, not a re-wrapped generic section heading. Do not exceed 5-10 FAQs per page to avoid Google devaluation.*

100 highly targeted FAQs injected contextually:
1. **Homepage (`index.html`)** - Brand & Trust FAQs (Mentioning Omear Memon).
2. **Employer Page (`/employer.html`)** - B2B & Fees FAQs.
3. **Jobs Page (`/jobs`)** - Industry Specific FAQs.
4. **Register Page (`/register`)** - Candidate Process FAQs.

---

## 🔍 7. Keyword Ontology & DefinedTermSet
Target terms formally defined in schema:
- Best HR Consultancy in Ahmedabad
- Bulk Hiring Solutions
- Free Placement Agency Ahmedabad
