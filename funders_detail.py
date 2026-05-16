"""Detailed information about the people behind each EA funder.

This is loaded by build_canvas.py / build_html.py / build_preview.py to enrich
each funder node with the principal donors, founders, and program leads.

Fields per funder id:
  - donors: list of {name, role, source} — principal funders & founders
  - leads:  list of {name, role}         — operational leadership / fund managers
  - founded: year (int) or None
  - typical_volume: rough annual giving volume (string), or None
  - notes: free-text caveat or context
  - source_url: a primary public source for verification
"""

FUNDER_PEOPLE = {

    "op": {
        "donors": [
            {"name": "Dustin Moskovitz", "role": "Co-funder", "source": "Co-founder of Facebook & Asana"},
            {"name": "Cari Tuna",        "role": "Co-funder", "source": "President of Good Ventures"},
        ],
        "leads": [
            {"name": "Alexander Berger", "role": "Co-CEO (Global Catastrophic Risks)"},
            {"name": "Emily Oehlsen",    "role": "Co-CEO (Global Health & Wellbeing)"},
        ],
        "founded": 2017,
        "typical_volume": "~$400M+/year",
        "notes": "Vehicle for Moskovitz/Tuna giving via Good Ventures. Biggest single funder in the EA ecosystem.",
        "source_url": "https://www.openphilanthropy.org/about/",
    },

    "sff": {
        "donors": [
            {"name": "Jaan Tallinn", "role": "Primary backer", "source": "Skype & Kazaa co-founder"},
            {"name": "Jed McCaleb",  "role": "Backer",         "source": "Stellar & eDonkey co-founder"},
        ],
        "leads": [
            {"name": "Andrew Critch",  "role": "Founder of S-process / SFF format"},
            {"name": "Oliver Habryka", "role": "Frequent recommender (Lightcone)"},
        ],
        "founded": 2019,
        "typical_volume": "~$20–40M/year",
        "notes": "Uses the 'S-process' — recommenders allocate among themselves rather than a single committee.",
        "source_url": "https://survivalandflourishing.fund/",
    },

    "ltff": {
        "donors": [
            {"name": "Open Philanthropy", "role": "Major backer", "source": "OP grants into the fund"},
            {"name": "Individual EA donors", "role": "Pool",       "source": "Small-dollar pledged giving"},
        ],
        "leads": [
            {"name": "Adam Gleave",    "role": "Fund manager (FAR AI)"},
            {"name": "Asya Bergal",    "role": "Fund manager (Open Phil)"},
            {"name": "Caleb Parikh",   "role": "Fund manager (EA Funds)"},
            {"name": "Linchuan Zhang", "role": "Fund manager"},
        ],
        "founded": 2017,
        "typical_volume": "~$5–10M/year",
        "notes": "Specialises in independent AI alignment researchers and small/new orgs.",
        "source_url": "https://funds.effectivealtruism.org/funds/far-future",
    },

    "eaif": {
        "donors": [
            {"name": "Open Philanthropy",     "role": "Major backer", "source": "OP grants into the fund"},
            {"name": "Individual EA donors",  "role": "Pool",          "source": "Small-dollar pledged giving"},
        ],
        "leads": [
            {"name": "Caleb Parikh",  "role": "Fund manager"},
            {"name": "Various rotating managers", "role": "Granting committee"},
        ],
        "founded": 2017,
        "typical_volume": "~$3–6M/year",
        "notes": "EA university groups, movement-building infrastructure, regranting.",
        "source_url": "https://funds.effectivealtruism.org/funds/ea-community",
    },

    "awf": {
        "donors": [
            {"name": "Open Philanthropy",    "role": "Major backer", "source": "OP grants into the fund"},
            {"name": "Individual EA donors", "role": "Pool",          "source": "Small-dollar pledged giving"},
        ],
        "leads": [
            {"name": "Karolina Sarek",   "role": "Fund manager (AIM founder)"},
            {"name": "Neil Dullaghan",   "role": "Fund manager (Rethink Priorities)"},
            {"name": "Toni Adleberg",    "role": "Fund manager"},
        ],
        "founded": 2017,
        "typical_volume": "~$4–8M/year",
        "notes": "Pure animal welfare focus — corporate campaigns, alt-protein, neglected species.",
        "source_url": "https://funds.effectivealtruism.org/funds/animal-welfare",
    },

    "ghdf": {
        "donors": [
            {"name": "Individual EA donors", "role": "Pool", "source": "Small-dollar pledged giving"},
        ],
        "leads": [
            {"name": "Defers to GiveWell research", "role": "Allocation"},
        ],
        "founded": 2017,
        "typical_volume": "~$2–5M/year",
        "notes": "Effectively a wrapper that allocates to GiveWell-recommended charities.",
        "source_url": "https://funds.effectivealtruism.org/funds/global-development",
    },

    "ftx": {
        "donors": [
            {"name": "Sam Bankman-Fried", "role": "Primary funder", "source": "FTX / Alameda (collapsed)"},
            {"name": "Gary Wang",         "role": "FTX co-founder", "source": "FTX equity"},
            {"name": "Caroline Ellison",  "role": "Alameda CEO",     "source": "Alameda profits"},
        ],
        "leads": [
            {"name": "Nick Beckstead",        "role": "CEO of Future Fund"},
            {"name": "William MacAskill",     "role": "Advisor"},
            {"name": "Leopold Aschenbrenner", "role": "Advisor"},
            {"name": "Ketan Ramakrishnan",    "role": "Advisor"},
            {"name": "Avital Balwit",         "role": "Advisor"},
        ],
        "founded": 2022,
        "typical_volume": "Pre-dissolution: ~$160M deployed; dissolved Nov 2022",
        "notes": "Resigned en bloc on FTX collapse. Many grants subject to clawback by bankruptcy estate.",
        "source_url": "https://web.archive.org/web/20221007135907/https://ftxfuturefund.org/",
    },

    "longview": {
        "donors": [
            {"name": "Donor-advised — multiple HNW backers", "role": "Anonymous + named", "source": "Various"},
        ],
        "leads": [
            {"name": "Natalie Cargill",   "role": "CEO & co-founder"},
            {"name": "Simran Dhaliwal",   "role": "Co-founder"},
        ],
        "founded": 2020,
        "typical_volume": "~$50M+/year (advised)",
        "notes": "Advisory firm for HNW longtermism donors. Programs include AI, biosecurity, nuclear.",
        "source_url": "https://www.longview.org/",
    },

    "givewell": {
        "donors": [
            {"name": "Open Philanthropy",       "role": "Major backer", "source": "OP routes large grants via GiveWell research"},
            {"name": "Individual public donors","role": "Mass pool",     "source": "Recurring + one-off donations"},
        ],
        "leads": [
            {"name": "Elie Hassenfeld", "role": "CEO & co-founder"},
            {"name": "Holden Karnofsky","role": "Co-founder (now at Anthropic)"},
        ],
        "founded": 2007,
        "typical_volume": "~$500M+/year directed",
        "notes": "Research-driven charity evaluator; donor flow > $500M annually to recommended top charities.",
        "source_url": "https://www.givewell.org/about",
    },

    "fp": {
        "donors": [
            {"name": "Tech founders / pledgers", "role": "Pledge community", "source": "Mostly exit liquidity"},
        ],
        "leads": [
            {"name": "David Goldberg", "role": "Co-founder & CEO"},
            {"name": "Matt Wage",       "role": "Head of Research"},
        ],
        "founded": 2015,
        "typical_volume": "~$1B+ pledged cumulatively",
        "notes": "Members pledge a portion of future exit proceeds. Operates multiple thematic funds.",
        "source_url": "https://founderspledge.com/about",
    },

    "ev": {
        "donors": [
            {"name": "Open Philanthropy", "role": "Major operational funder", "source": "Sustaining grants"},
            {"name": "Various", "role": "Project-level funding flows in via hosted projects", "source": "—"},
        ],
        "leads": [
            {"name": "Zachary Robinson", "role": "CEO (CEA / EV US)"},
            {"name": "EV UK + EV US boards", "role": "Trustees"},
        ],
        "founded": 2011,
        "typical_volume": "Fiscal sponsor — not a primary funder",
        "notes": "Umbrella legal entity for CEA, 80K, GWWC, EA Funds, GovAI, BlueDot, Longview, Forethought, etc. Split UK/US after FTX.",
        "source_url": "https://www.ev.org/",
    },

    "tallinn": {
        "donors": [
            {"name": "Jaan Tallinn", "role": "Sole funder", "source": "Skype & Kazaa co-founder"},
        ],
        "leads": [
            {"name": "Jaan Tallinn", "role": "Personal decisions; also routes via SFF & FLI board"},
        ],
        "founded": None,
        "typical_volume": "Tens of millions / year across SFF + personal",
        "notes": "Lifetime giving pledge focused on x-risk reduction.",
        "source_url": "https://jaan.online/",
    },

    "buterin": {
        "donors": [
            {"name": "Vitalik Buterin", "role": "Sole funder", "source": "Ethereum founder"},
        ],
        "leads": [
            {"name": "Vitalik Buterin", "role": "Personal decisions"},
        ],
        "founded": None,
        "typical_volume": "Variable; large episodic gifts (e.g., $665M Methuselah, SENS)",
        "notes": "Mostly longevity & x-risk adjacent; not core EA but often overlaps.",
        "source_url": "https://vitalik.eth.limo/",
    },

    "macro": {
        "donors": [
            {"name": "Brendan Mead", "role": "Founder", "source": "Crypto wealth"},
        ],
        "leads": [
            {"name": "Brendan Mead", "role": "Principal"},
        ],
        "founded": 2021,
        "typical_volume": "~$5–15M/year (estimated)",
        "notes": "Smaller funder; AI safety & biosecurity grants alongside SFF.",
        "source_url": "https://www.macroscopicventures.com/",
    },

    "astera": {
        "donors": [
            {"name": "Jed McCaleb", "role": "Founder", "source": "Stellar / eDonkey wealth"},
        ],
        "leads": [
            {"name": "Sam Rodriques", "role": "President"},
            {"name": "Jed McCaleb",   "role": "Funder & strategist"},
        ],
        "founded": 2021,
        "typical_volume": "~$100M committed, multi-year",
        "notes": "Mostly metascience / FROs / beneficial science. EA-adjacent on AI safety.",
        "source_url": "https://astera.org/",
    },

    "schmidt": {
        "donors": [
            {"name": "Eric Schmidt",  "role": "Co-funder", "source": "Ex-CEO Google / Alphabet"},
            {"name": "Wendy Schmidt", "role": "Co-funder", "source": "Schmidt Family Foundation"},
        ],
        "leads": [
            {"name": "Stuart Feldman", "role": "Chief Scientist"},
            {"name": "Tom Kalil",      "role": "Chief Innovation Officer (formerly)"},
        ],
        "founded": 2017,
        "typical_volume": "~$300M+/year across all Schmidt vehicles",
        "notes": "Broad science philanthropy; intersects EA via AI safety & biosecurity programs.",
        "source_url": "https://www.schmidtfutures.com/",
    },

    "aim": {
        "donors": [
            {"name": "Open Philanthropy",   "role": "Major backer", "source": "OP recommended grant"},
            {"name": "Founders Pledge",      "role": "Backer",       "source": "FP recommendation"},
            {"name": "Individual EA donors", "role": "Pool"},
        ],
        "leads": [
            {"name": "Joey Savoie",     "role": "Co-founder & CEO"},
            {"name": "Karolina Sarek",  "role": "Co-founder"},
        ],
        "founded": 2018,
        "typical_volume": "~$3M/year (operations) + incubates new charities",
        "notes": "Incubator that spawns multiple new EA charities annually (Charity Entrepreneurship rebranded to AIM in 2024).",
        "source_url": "https://www.charityentrepreneurship.com/",
    },

}
