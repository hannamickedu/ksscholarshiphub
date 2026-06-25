"""
Scholarship Hub — Weekly Updater
Runs every Monday at 7 AM CT via GitHub Actions.
Pulls from free public sources. No API key required.
"""

import json
import requests
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET

# ── Permanent scholarship database ─────────────────────────────────────────
# These are well-known recurring scholarships with stable deadlines.
# Update this list as needed when scholarships change.
PERMANENT_SCHOLARSHIPS = [
    {
        "name": "Kansas State Scholarship",
        "amount": "Up to $1,000/yr",
        "description": "State-funded award for Kansas residents demonstrating financial need. Renewable for up to 4 years at accredited Kansas colleges and universities.",
        "sponsor": "Kansas Board of Regents",
        "deadline": "2026-07-01",
        "tags": ["kansas", "need"],
        "url": "https://www.kansasregents.org/students/student_financial_aid/scholarships_and_grants"
    },
    {
        "name": "Kansas Ethnic Minority Scholarship",
        "amount": "Up to $1,850/yr",
        "description": "For academically talented minority students who are Kansas residents, enrolled or planning to enroll at a Kansas postsecondary institution.",
        "sponsor": "Kansas Board of Regents",
        "deadline": "2026-04-01",
        "tags": ["kansas", "need", "firstgen"],
        "url": "https://www.kansasregents.org/students/student_financial_aid/scholarships_and_grants"
    },
    {
        "name": "Kansas 4-H Foundation Scholarship",
        "amount": "$1,000–$2,500",
        "description": "For Kansas students who have been active 4-H members for at least 3 years. Preference given to students continuing involvement in agriculture or community development.",
        "sponsor": "Kansas 4-H Foundation",
        "deadline": "2026-02-01",
        "tags": ["kansas", "merit"],
        "url": "https://kansas4hfoundation.org/scholarships/"
    },
    {
        "name": "Coca-Cola Scholars Program",
        "amount": "$20,000",
        "description": "One of the most prestigious national scholarships for high school seniors. Merit-based, awarded to 150 students annually. Strong community leadership record required.",
        "sponsor": "Coca-Cola Foundation",
        "deadline": "2026-10-15",
        "tags": ["national", "merit"],
        "url": "https://www.coca-colascholarsfoundation.org/apply/"
    },
    {
        "name": "Gates Scholarship",
        "amount": "Full cost of attendance",
        "description": "Highly selective scholarship for exceptional minority students with significant financial need. Covers full cost of attendance at any U.S. college. Includes leadership development.",
        "sponsor": "Bill & Melinda Gates Foundation",
        "deadline": "2026-09-01",
        "tags": ["national", "need", "firstgen"],
        "url": "https://www.thegatesscholarship.org/scholarship"
    },
    {
        "name": "Horatio Alger National Scholarship",
        "amount": "$25,000",
        "description": "For students who have overcome great obstacles. Applicants must demonstrate integrity, perseverance, and financial need. One of the largest need-based scholarships available.",
        "sponsor": "Horatio Alger Association",
        "deadline": "2026-10-25",
        "tags": ["national", "need", "firstgen"],
        "url": "https://scholars.horatioalger.org/scholarships/about-our-scholarship-programs/"
    },
    {
        "name": "Ron Brown Scholar Program",
        "amount": "$40,000 (over 4 years)",
        "description": "Academically gifted African American students who display exceptional leadership potential, participate in community service, and demonstrate financial need.",
        "sponsor": "Ron Brown Scholar Fund",
        "deadline": "2026-01-09",
        "tags": ["national", "merit", "need", "firstgen"],
        "url": "https://www.ronbrown.org/section/apply/program-description"
    },
    {
        "name": "Davidson Fellows Scholarship",
        "amount": "$10,000–$50,000",
        "description": "For students 18 and under who have completed a significant piece of work in science, technology, engineering, mathematics, literature, music, or philosophy.",
        "sponsor": "Davidson Institute",
        "deadline": "2026-02-11",
        "tags": ["national", "stem", "arts", "merit"],
        "url": "https://www.davidsongifted.org/gifted-programs/fellows-scholarship/"
    },
    {
        "name": "Elks National Foundation Most Valuable Student",
        "amount": "$4,000–$50,000",
        "description": "One of the largest scholarship competitions in the country. Open to U.S. citizens in their final year of high school. Based on scholarship, leadership, and financial need.",
        "sponsor": "Elks National Foundation",
        "deadline": "2026-11-08",
        "tags": ["national", "merit", "need"],
        "url": "https://www.elks.org/scholars/scholarships/mvs.cfm"
    },
    {
        "name": "Burger King Scholars Program",
        "amount": "Up to $50,000",
        "description": "Open to high school seniors. No minimum GPA required — focuses on community service and financial need. Very accessible application process.",
        "sponsor": "Burger King McLamore Foundation",
        "deadline": "2026-12-15",
        "tags": ["national", "need"],
        "url": "https://www.bkmclamorefoundation.org/apply"
    },
    {
        "name": "Prudential Spirit of Community Award",
        "amount": "$1,000 + trip to Washington D.C.",
        "description": "Honors high school students for outstanding volunteer service. Each state selects two Distinguished Finalists who each receive $1,000.",
        "sponsor": "Prudential Financial",
        "deadline": "2026-11-05",
        "tags": ["national", "merit"],
        "url": "https://spirit.prudential.com/"
    },
    {
        "name": "Tylenol Future Care Scholarship",
        "amount": "$5,000–$10,000",
        "description": "For students pursuing a career in healthcare. Strong community service record encouraged. Open to high school seniors and current college students.",
        "sponsor": "Tylenol / Johnson & Johnson",
        "deadline": "2026-06-30",
        "tags": ["national", "stem"],
        "url": "https://www.tylenol.com/news/scholarship"
    },
    {
        "name": "Kansas City Royals Baseball Scholarship",
        "amount": "$2,000",
        "description": "For graduating high school seniors in the greater Kansas City area demonstrating academic achievement, financial need, and community involvement.",
        "sponsor": "Kansas City Royals Charities",
        "deadline": "2026-02-28",
        "tags": ["kansas", "need"],
        "url": "https://www.mlb.com/royals/community/charities"
    },
    {
        "name": "KCUR/Missouri Valley Journalism Scholarship",
        "amount": "$2,000",
        "description": "For Kansas and Missouri students pursuing journalism, communications, or media studies. Includes mentorship with KCUR public radio staff.",
        "sponsor": "KCUR Public Media",
        "deadline": "2026-01-31",
        "tags": ["kansas", "arts"],
        "url": "https://www.kcur.org/"
    },
]


def fetch_fastweb_rss():
    """
    Fetches from Fastweb's public RSS feed for new scholarship listings.
    Returns a list of scholarship dicts (best-effort parsing).
    """
    rss_urls = [
        "https://www.fastweb.com/rss/scholarships.xml",
    ]
    results = []
    headers = {"User-Agent": "ScholarshipHub/1.0 (educational use)"}

    for url in rss_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"  RSS fetch failed ({resp.status_code}): {url}")
                continue

            root = ET.fromstring(resp.content)
            items = root.findall(".//item")
            print(f"  Found {len(items)} items in RSS feed")

            for item in items[:10]:  # Cap at 10 new items
                title = (item.findtext("title") or "").strip()
                link  = (item.findtext("link") or "").strip()
                desc  = (item.findtext("description") or "").strip()
                if title and link:
                    results.append({
                        "name": title,
                        "amount": "Varies",
                        "description": desc[:300] if desc else "Visit scholarship page for full details.",
                        "sponsor": "Fastweb listing",
                        "deadline": "2026-12-31",
                        "tags": ["national"],
                        "url": link,
                        "_source": "rss"
                    })
        except Exception as e:
            print(f"  RSS error: {e}")

    return results


def filter_active(scholarships):
    """Remove scholarships whose deadlines have already passed."""
    today = datetime.now(timezone.utc).date()
    active = []
    for s in scholarships:
        try:
            deadline = datetime.fromisoformat(s["deadline"]).date()
            if deadline >= today:
                active.append(s)
        except Exception:
            active.append(s)  # Keep if we can't parse the date
    return active


def deduplicate(scholarships):
    """Remove duplicates by name (case-insensitive)."""
    seen = set()
    unique = []
    for s in scholarships:
        key = s["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def sort_by_deadline(scholarships):
    """Sort scholarships: soonest deadline first."""
    def sort_key(s):
        try:
            return datetime.fromisoformat(s["deadline"])
        except Exception:
            return datetime(2099, 12, 31)
    return sorted(scholarships, key=sort_key)


def main():
    print("=" * 50)
    print(f"Scholarship Hub — Weekly Update")
    print(f"Running at: {datetime.now().strftime('%Y-%m-%d %H:%M')} CT")
    print("=" * 50)

    # Start with the permanent list
    all_scholarships = list(PERMANENT_SCHOLARSHIPS)
    print(f"\n✓ Loaded {len(all_scholarships)} permanent scholarships")

    # Try to pull fresh listings from RSS feeds
    print("\nFetching from public scholarship feeds...")
    rss_scholarships = fetch_fastweb_rss()
    if rss_scholarships:
        print(f"✓ Retrieved {len(rss_scholarships)} listings from RSS")
        all_scholarships.extend(rss_scholarships)
    else:
        print("  (No RSS items added — using permanent list)")

    # Clean up
    all_scholarships = deduplicate(all_scholarships)
    all_scholarships = filter_active(all_scholarships)
    all_scholarships = sort_by_deadline(all_scholarships)

    print(f"\n✓ Final count: {len(all_scholarships)} active scholarships")

    # Build the output
    now_ct = datetime.now(timezone(timedelta(hours=-5)))  # CST offset
    output = {
        "last_updated": now_ct.isoformat(),
        "scholarships": all_scholarships
    }

    with open("scholarships.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ scholarships.json written successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()
