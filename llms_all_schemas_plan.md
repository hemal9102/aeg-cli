# `llms.php` - All Schemas Injection Plan

Aapne decide kiya hai ki `llms.txt` (jo `llms.php` se serve ho raha hai) mein website ki **Saari ki Saari Schemas** (B2B Employer + Har ek Live Job) aani chahiye. Isse ChatGPT/Perplexity ek hi baar mein poori website ka data scrape kar lega.

Neeche wo exact PHP code diya gaya hai jo main `C:\hk\_public_html\backend\api\llms.php` ke sabse end mein add karunga. Aap isko review kar lijiye.

## 1. B2B Employer Schema Code
Ye code Omear Memon as founder aur Corporate Hiring (B2B) ka tag attach karega:

```php
echo "### B2B Employer Schema (Corporate Hiring)\\n";
$b2bSchema = [
    "@context" => "https://schema.org",
    "@type" => ["B2BBusiness", "HRConsulting", "EmploymentAgency"],
    "@id" => "https://jobrecruitment.in/employer.html#b2b",
    "name" => "Job Recruitment - Corporate Hiring Services",
    "founder" => [
        "@type" => "Person",
        "name" => "Omear Memon"
    ],
    "description" => "Executive search, bulk hiring, and IT staffing solutions for enterprises in Ahmedabad.",
    "areaServed" => "Ahmedabad, Gujarat, India",
    "url" => "https://jobrecruitment.in/employer.html",
    "telephone" => "+91-9099876985"
];
echo "```json\\n";
echo json_encode($b2bSchema, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
echo "\\n```\\n\\n";
```

## 2. All Active `JobPosting` Schemas (Live DB Dump)
Ye code PHP ki memory crash kiye bina, Database se ek-ek karke saari `Active` jobs uthayega aur unhe `JobPosting` JSON-LD schema mein format karke AI bot ko bhej dega:

```php
echo "### ALL Active JobPosting Schemas (Massive Database Dump)\\n";
echo "```json\\n";
echo "[\\n";

try {
    // Stream output to avoid PHP Memory Limits with 4500+ rows
    $stmt = $pdo->query("SELECT * FROM jobs WHERE deleted_at IS NULL AND status = 'Active'");
    $first = true;
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        if (!$first) {
            echo ",\\n";
        }
        $first = false;
        
        $jobSchema = [
            "@context" => "https://schema.org",
            "@type" => "JobPosting",
            "title" => $row['job_role'] ?? 'Job Opening',
            "description" => $row['description'] ?? 'Job details available upon contact.',
            "datePosted" => date('c', strtotime($row['date_posted'] ?? date('Y-m-d'))),
            "validThrough" => date('c', strtotime('+6 months')),
            "employmentType" => $row['employment_type'] ?? 'FULL_TIME',
            "hiringOrganization" => [
                "@type" => "Organization",
                "name" => $row['company_name'] ?? 'Confidential Client'
            ],
            "jobLocation" => [
                "@type" => "Place",
                "address" => [
                    "@type" => "PostalAddress",
                    "addressLocality" => $row['location'] ?? 'Ahmedabad',
                    "addressRegion" => "Gujarat",
                    "addressCountry" => "IN"
                ]
            ],
            "baseSalary" => [
                "@type" => "MonetaryAmount",
                "currency" => "INR",
                "value" => [
                    "@type" => "QuantitativeValue",
                    "value" => $row['salary_range'] ?? 'Competitive',
                    "unitText" => "MONTH"
                ]
            ]
        ];
        
        echo json_encode($jobSchema, JSON_UNESCAPED_SLASHES);
    }
} catch (Exception $e) {
    // Safely ignore if DB schema mismatches
}

echo "\\n]\\n```\\n";
```

### Risk Warning (Jiska maine pehle zikra kiya tha):
Agar database mein 4000+ jobs hue, toh `llms.txt` ka size **10MB se 20MB** tak ho sakta hai. Agar aap ye code confirm karte hain, toh main ise seedha execute kar dunga!
