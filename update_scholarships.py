import json
import os
import anthropic
from datetime import datetime, timezone, timedelta

PERMANENT_SCHOLARSHIPS = [
    {"name":"Kansas State Scholarship","amount":"Up to $1,000/yr","description":"State-funded award for Kansas residents demonstrating financial need. Renewable for up to 4 years at accredited Kansas colleges and universities.","sponsor":"Kansas Board of Regents","deadline":"2026-07-01","tags":["kansas","need"],"url":"https://www.kansasregents.org/students/student_financial_aid/scholarships_and_grants"},
    {"name":"Coca-Cola Scholars Program","amount":"$20,000","description":"One of the most prestigious national scholarships for high school seniors. Merit-based, awarded to 150 students annually. Strong community leadership record required.","sponsor":"Coca-Cola Foundation","deadline":"2026-10-15","tags":["national","merit"],"url":"https://www.coca-colascholarsfoundation.org/apply/"},
    {"name":"Gates Scholarship","amount":"Full cost of attendance","description":"Highly selective scholarship for exceptional minority students with significant financial need. Covers full cost of attendance at any U.S. college.","sponsor":"Bill & Melinda Gates Foundation","deadline":"2026-09-01","tags":["national","need","firstgen"],"url":"https://www.thegatesscholarship.org/scholarship"},
    {"name":"Kansas 4-H Foundation Scholarship","amount":"$1,000-$2,500","description":"For Kansas students who have been active 4-H members for at least 3 years. Preference given to students continuing involvement in agriculture or community development.","sponsor":"Kansas 4-H Foundation","deadline":"2027-02-01","tags":["kansas","merit"],"url":"https://kansas4hfoundation.org/scholarships/"},
    {"name":"Horatio Alger National Scholarship","amount":"$25,000","description":"For students who have overcome great obstacles. Applicants must demonstrate integrity, perseverance, and financial need.","sponsor":"Horatio Alger Association","deadline":"2026-10-25","tags":["national","need","firstgen"],"url":"https://scholars.horatioalger.org/scholarships/about-our-scholarship-programs/"},
    {"name":"Burger King Scholars Program","amount":"Up to $50,000","description":"Open to high school seniors. No minimum GPA required - focuses on community service and financial need. Very accessible application.","sponsor":"Burger King McLamore Foundation","deadline":"2026-12-15","tags":["national","need"],"url":"https://www.bkmclamorefoundation.org/apply"},
    {"name":"Davidson Fellows Scholarship","amount":"$10,000-$50,000","description":"For students 18 and under who have completed a significant piece of work in science, technology, engineering, mathematics, literature, music, or philosophy.","sponsor":"Davidson Institute","deadline":"2027-02-11","tags":["national","stem","arts","merit"],"url":"https://www.davidsongifted.org/gifted-programs/fellows-scholarship/"},
    {"name":"Ron Brown Scholar Program","amount":"$40,000 over 4 years","description":"Academically gifted African American students who display exceptional leadership potential, participate in community service, and demonstrate financial need.","sponsor":"Ron Brown Scholar Fund","deadline":"2027-01-09","tags":["national","merit","need","firstgen"],"url":"https://www.ronbrown.org/section/apply/program-description"},
    {"name":"Prudential Spirit of Community Award","amount":"$1,000 plus trip to Washington DC","description":"Honors high school students for outstanding volunteer service. Each state selects two Distinguished Finalists who receive $1,000 each.","sponsor":"Prudential Financial","deadline":"2026-11-05","tags":["national","merit"],"url":"https://spirit.prudential.com/"},
    {"name":"Kansas Ethnic Minority Scholarship","amount":"Up to $1,850/yr","description":"For academically talented minority students who are Kansas residents enrolled or planning to enroll at a Kansas postsecondary institution.","sponsor":"Kansas Board of Regents","deadline":"2027-04-01","tags":["kansas","need","firstgen"],"url":"https://www.kansasregents.org/students/student_financial_aid/scholarships_and_grants"},
    {"name":"Elks National Foundation Most Valuable Student","amount":"$4,000-$50,000","description":"One of the largest scholarship competitions in the country. Open to U.S. citizens in their final year of high school. Based on scholarship, leadership, and financial need.","sponsor":"Elks National Foundation","deadline":"2026-11-08","tags":["national","merit","need"],"url":"https://www.elks.org/scholars/scholarships/mvs.cfm"},
    {"name":"Tylenol Future Care Scholarship","amount":"$5,000-$10,000","description":"For students pursuing a career in healthcare. Open to high school seniors and current college students.","sponsor":"Tylenol / Johnson and Johnson","deadline":"2026-06-30","tags":["national","stem"],"url":"https://www.tylenol.com/news/scholarship"},
    {"name":"Kansas City Royals Baseball Scholarship","amount":"$2,000","description":"For graduating high school seniors in the greater Kansas City area demonstrating academic achievement, financial need, and community involvement.","sponsor":"Kansas City Royals Charities","deadline":"2027-02-28","tags":["kansas","need"],"url":"https://www.mlb.com/royals/community/charities"},
    {"name":"KCUR Missouri Valley Journalism Scholarship","amount":"$2,000","description":"For Kansas and Missouri students pursuing journalism, communications, or media studies. Includes mentorship with KCUR public radio staff.","sponsor":"KCUR Public Media","deadline":"2027-01-31","tags":["kansas","arts"],"url":"https://www.kcur.org/"},
    {"name":"Hispanic Scholarship Fund","amount":"$500-$5,000","description":"For Hispanic students with a minimum 3.0 GPA pursuing a degree at an accredited U.S. college or university. Financial need is considered.","sponsor":"Hispanic Scholarship Fund","deadline":"2027-02-15","tags":["national","need","firstgen"],"url":"https://www.hsf.net/scholarship"},
    {"name":"Dell Scholars Program","amount":"$20,000 plus laptop and support","description":"For students who demonstrate the drive to succeed despite facing difficult circumstances. Includes ongoing support resources through college.","sponsor":"Michael and Susan Dell Foundation","deadline":"2026-12-01","tags":["national","need","firstgen"],"url":"https://www.dellscholars.org/scholarship/"},
    {"name":"Scholly Scholarship Search","amount":"Varies","description":"Scholly matches students to hundreds of scholarships based on their background, interests, and goals. Free to search the database.","sponsor":"Scholly","deadline":"2026-12-31","tags":["national"],"url":"https://myscholly.com/"},
    {"name":"Fastweb Scholarship Database","amount":"Varies","description":"One of the largest free scholarship search databases. Create a profile and get matched to scholarships you qualify for.","sponsor":"Fastweb","deadline":"2026-12-31","tags":["national"],"url":"https://www.fastweb.com/"},
]


def fetch_ai_scholarships():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("No API key found - skipping AI search")
        return []

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime("%B %d, %Y")

    prompt = (
        "Today is " + today + ". You are helping update a scholarship website for Kansas high school students.\n\n"
        "Please provide 8-10 ADDITIONAL scholarships beyond the common well-known ones. Focus on:\n"
        "- Lesser-known but legitimate scholarships open to high school students\n"
        "- Kansas-specific scholarships from local foundations, businesses, or organizations\n"
        "- National scholarships for specific interests like agriculture, music, community service, or leadership\n"
        "- Scholarships with deadlines still upcoming as of today\n\n"
        "Respond with ONLY a JSON array. No explanation, no markdown, just the raw JSON array.\n"
        "Each item must have: name, amount, description, sponsor, deadline (YYYY-MM-DD), tags (array), url\n"
        "Tags must only be from: kansas, national, stem, arts, firstgen, merit, need, essay\n"
        "Use kansas for Kansas-specific, national for all others. Every item needs at least one tag.\n"
        "Only include scholarships you are confident are real with accurate URLs."
    )

    try:
        print("Asking Claude for additional scholarships...")
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scholarships = json.loads(raw.strip())
        print("Claude returned " + str(len(scholarships)) + " additional scholarships")
        return scholarships
    except Exception as e:
        print("AI search error: " + str(e))
        return []


def days_until(date_str):
    try:
        d = datetime.fromisoformat(date_str).date()
        return (d - datetime.now().date()).days
    except Exception:
        return 999


def deduplicate(scholarships):
    seen = set()
    unique = []
    for s in scholarships:
        key = s["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def filter_active(scholarships):
    return [s for s in scholarships if days_until(s.get("deadline", "2099-01-01")) >= 0]


def sort_by_deadline(scholarships):
    return sorted(scholarships, key=lambda s: s.get("deadline", "2099-12-31"))


def main():
    print("Scholarship Hub - Weekly Update")
    print("Running at: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Always start with the full permanent list
    all_scholarships = list(PERMANENT_SCHOLARSHIPS)
    print("Loaded " + str(len(all_scholarships)) + " permanent scholarships")

    # Add AI-discovered scholarships on top
    ai_scholarships = fetch_ai_scholarships()
    if ai_scholarships:
        all_scholarships.extend(ai_scholarships)
        print("Added " + str(len(ai_scholarships)) + " AI scholarships")

    # Remove duplicates (permanent list always wins since it's first)
    all_scholarships = deduplicate(all_scholarships)
    # Remove any with passed deadlines
    all_scholarships = filter_active(all_scholarships)
    # Sort soonest deadline first
    all_scholarships = sort_by_deadline(all_scholarships)

    print("Final count: " + str(len(all_scholarships)) + " active scholarships")

    now_ct = datetime.now(timezone(timedelta(hours=-5))).isoformat()
    output = {"last_updated": now_ct, "scholarships": all_scholarships}

    with open("scholarships.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Done! scholarships.json updated.")


if __name__ == "__main__":
    main()
