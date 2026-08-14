# VERIFIED boards only (impostor slugs removed after ownership check).
# (firm, ats, slug)   workday slug = "tenant.wdN/site"
FIRMS = [
    # --- large private credit platforms (verified) ---
    ("Ares Management", "workday", "aresmgmt.wd1/External"),
    ("Blue Owl Capital", "workday", "blueowl.wd1/blueowl"),
    ("Oaktree Capital Management", "workday", "oaktree.wd1/Oaktree"),
    ("Golub Capital", "workday", "golubcapital.wd5/golub_capital_careers"),
    ("Sixth Street", "greenhouse", "sixthstreet"),
    ("ORIX USA", "workday", "orix.wd5/External_ORIX"),
    ("Moelis & Company", "workday", "moelis.wd1/Experienced-Hires"),
    ("Franklin Templeton / Benefit Street Partners", "workday", "franklintempleton.wd5/Invitation-Only"),
    ("BlackRock (incl. HPS Investment Partners)", "workday", "blackrock.wd1/BlackRock_Professional"),
    ("Angelo Gordon (TPG)", "workday", "angelogordon.wd1/angelogordoncareers"),
    ("PRA Group, Inc.", "workday", "pra.wd1/PRA_Careers"),
    # --- mid/small managers (verified) ---
    ("Star Mountain Capital", "greenhouse", "starmountaincapital"),
    ("Redding Ridge Asset Management", "greenhouse", "reddingridge"),
    ("Sound Point Capital Management", "greenhouse", "soundpointcapital"),
    ("Lafayette Square", "greenhouse", "lafayettesquare"),
    ("MonticelloAM", "greenhouse", "monticelloam"),
    ("Pagaya Technologies", "greenhouse", "pagaya"),
    ("Point Digital Finance", "greenhouse", "pointdigitalfinance"),
    ("Spotter, Inc.", "greenhouse", "spotter"),
    ("Waterfall Asset Management", "lever", "waterfall"),
    ("Eagle Point Credit Management", "lever", "eaglepointcredit"),
    ("Prospect Administration (Prospect Capital)", "bamboohr", "prospect"),
    ("Specialty Capital", "bamboohr", "specialtycapital"),
    ("Enhanced Capital Holdings", "bamboohr", "enhanced"),
    ("VWH Capital Management", "smartrecruiters", "vwhcapitalmanagementlp"),
    ("Wayflyer", "ashby", "wayflyer"),
    ("Capchase", "ashby", "capchase"),
]

# Boards in the source table that resolved to a DIFFERENT company - excluded, do not trust.
IMPOSTORS = {
    "White Oak Global Advisors": "greenhouse:whiteoak -> White Oak Veterinary Clinic",
    "Percent / Cadence Group": "workday:cadence.wd1 -> Cadence Design Systems (semiconductors)",
    "Community Investment Management": "greenhouse:community -> Rome Community Partners",
    "Panagram Services": "greenhouse:psl -> 'Pearson Spectre Litt'",
    "Park Square Capital USA": "workday:park.wd1/ParkUniversityCareers -> Park University",
    "Antares Capital LP": "ashby:antares -> LA thermal/fluids engineering firm",
    "Silver Rock Capital Partners": "ashby:silver -> Silver.dev (Argentina dev recruiting)",
    "Phoenix Merchant Partners": "ashby:phoenix -> Canadian pharmacy chain",
    "Arena Investors": "ashby:arena -> Bay Area tech recruiting",
    "Black Diamond Capital Management": "recruitee:blackdiamond -> sales/recruiting internships (Andover MA)",
    "Metropolitan Partners Group": "pinpoint:mmgapts -> Metropolitan Companies (apartments, PA)",
    "Runway Growth Capital": "ashby:runway -> Runway (AI/ML company)",
    "FIG LLC / Fortress": "ashby:fig -> single 'Test job' in SF, not Fortress",
    "Hercules Capital": "ashby:hercules -> unrelated SF/remote tech co",
}
