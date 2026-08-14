import os

LLMS_FILE = r"C:\hk\_public_html\backend\api\llms.php"

with open(LLMS_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# We need to append the Job Schemas and B2B Schema at the end.
# The file ends with:
# echo "```json\n";
# echo json_encode($faqs, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
# echo "\n```\n";

if "### B2B Employer Schema" not in content:
    addition = """
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
    // If table structure differs, just ignore and don't break the JSON output
}

echo "\\n]\\n```\\n";
"""
    content = content + addition
    with open(LLMS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

print("llms.php updated to include ALL active job schemas!")
