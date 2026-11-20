"""Builds backend/seed_data.json from text captured from the public pages.

The seed is a fallback snapshot so the chatbot always has real content, even if the
live scraper is blocked from the hosting provider's IP. Run: python backend/make_seed.py
"""
import json
import pathlib

D = "DarGlobal"
W = "Wasalt"
docs = []


def add(source, title, url, text, origin="captured"):
    docs.append(dict(source=source, title=title, url=url, content=text.strip(), origin=origin))


add(D, "DarGlobal – company overview", "https://darglobal.co.uk/", """
DarGlobal (Dar Global) is a London-listed luxury real estate developer, investor and asset manager. Its tagline is "Global Capital. Enduring Places." It creates high-quality communities, landmark destinations and lifestyle-driven assets across premier global markets including the UAE, Saudi Arabia, Qatar, Spain and London, spanning premium hospitality, commercial, entertainment and exclusive golf communities.
DarGlobal owns, invests in, develops and operates high-end real estate, combining global partnerships, strong fundamentals and disciplined execution.
Headline figures shown on the homepage (indicative, aligned with disclosures as of Q3 2026): 32 years track record; USD 23 billion gross development value; 7 international markets; 12+ global brand partners.
About: DarGlobal describes itself as a premier international luxury real estate investment and development platform specialising in architecturally distinctive, design-led residences in the world's most sought-after destinations. It is listed on the London Stock Exchange and its portfolio spans masterplanned communities, branded luxury apartments and hospitality-led destinations developed with partners from automotive, fashion and hospitality.
Featured projects on the homepage: AIDA (Oman masterplan, described as one of the world's largest premium mixed-use developments); Trump International Simaisma, Qatar; Trump Mansions, Wadi Safar, Riyadh, Saudi Arabia.
""")

add(D, "DarGlobal – brand collaborations and partners", "https://darglobal.co.uk/partners/aston-martin", """
DarGlobal's homepage lists exclusive collaborations with: Aston Martin (The Astera beach home), Elie Saab, FENDI Casa, Automobili Lamborghini, Marriott (Marriott Residences AIDA Oman), Missoni, Mouawad, Pagani, The Trump Organization, W Residences by Marriott International (W Hotels), and Paramount. Partner pages are at darglobal.co.uk/partners/<name>, e.g. https://darglobal.co.uk/partners/aston-martin, /partners/elie-saab, /partners/fendi-casa, /partners/lamborghini, /partners/missoni, /partners/mouawad, /partners/pagani, /partners/the-trump-organization, /partners/w-hotels, /partners/paramount.
""")

add(D, "DarGlobal – business lines: communities, golf, hospitality, commercial", "https://darglobal.co.uk/luxury-golf-communities", """
Building Luxury Communities: DarGlobal creates fully integrated communities designed for long-term living, investment stability and enduring value, from masterplanned environments to ultra-exclusive residential enclaves across UAE and European markets, built around connectivity, luxury lifestyle and scarcity.
Hospitality & Leisure (https://darglobal.co.uk/hospitality): develops and operates hospitality-led assets with world-class global brands, combining location, brand power and operational excellence to create destinations that generate recurring income while enhancing surrounding real estate value.
Golf: a cornerstone of the community strategy, anchoring premium developments with globally recognised courses and club experiences, aimed at high-net-worth buyers of luxury villas in Spain and the Middle East.
Commercial (https://darglobal.co.uk/commercial): high-quality commercial assets designed to generate stable, recurring income, complementing residential portfolios including in Qatar.
Private membership (https://darglobal.co.uk/exclusive-membership): a new generation of private membership clubs across its global destinations, including an exclusive private members club in Jeddah, Saudi Arabia, and upcoming hospitality destinations in Dubai.
""")

add(D, "DarGlobal – asset management (DGCP) and tokenization", "https://darglobal.co.uk/investor", """
Asset management: Dar Global Capital Partners (DGCP) is the DFSA-regulated investment management subsidiary of DarGlobal, headquartered in the Dubai International Financial Centre (DIFC). DGCP deploys capital across global real estate markets, structuring opportunities in equity, debt and hybrid instruments across GCC, European and US gateway markets, for qualified investors and strategic partners. Investor relations: https://darglobal.co.uk/investor
Tokenization (https://darglobal.co.uk/tokenization): DarGlobal says it is pioneering new ways to access premium real estate through tokenization and digital ownership structures, aiming to improve liquidity, broaden investor access and create more efficient pathways into luxury real estate assets.
""")

add(D, "DarGlobal – newsroom highlights (Jun–Nov 2026)", "https://darglobal.co.uk/press", """
Recent DarGlobal press releases listed on its homepage:
- Nov 16, 2026: Dar Global expands Saudi Arabia portfolio with a new mixed-use development in Jeddah valued at SAR 1 billion (https://darglobal.co.uk/press/dar-global-expands-saudi-arabia-portfolio-with-new-jeddah-development-valued-at-sar-1-billion).
- Oct 26, 2026: Dar Global Capital Partners targets high-value real estate opportunities in Dubai (https://darglobal.co.uk/press/dar-global-capital-partners-targets-high-value-real-estate-opportunities-dubai).
- Oct 07, 2026: Dar Global opens sales for Trump Villas Simaisma, Qatar, within Trump International Golf Club Simaisma (https://darglobal.co.uk/press/dar-global-opens-sales-trump-villas-simaisma-qatar-unprecedented-interest).
- Sep 30, 2026: Dar Global reports 66% revenue growth in HY 2026, with portfolio GDV reaching USD 23 billion (https://darglobal.co.uk/press/dar-global-delivers-66-percent-revenue-growth-hy-2026-portfolio-gdv-reaches-23-billion).
- Aug 06, 2026: Gulf Asia Contracting appointed for the podium of Trump International Hotel & Tower, Dubai (https://darglobal.co.uk/press/dar-global-appoints-gulf-asia-contracting-for-trump-international-hotel-tower-dubai).
- Jun 29, 2026: Dar Global and Fendi Casa announce Azure Oceanfront Villas in Oman, within AIDA (https://darglobal.co.uk/press/darglobal-fendi-casa-announce-azure-oceanfront-villas-oman).
""")

add(D, "DarGlobal – project directory overview", "https://darglobal.co.uk/projects", """
DarGlobal's projects page lets visitors filter by type (Apartments, Villas, Hotel Rooms) and location (United Arab Emirates, Spain, Qatar, Oman, United Kingdom, Saudi Arabia). It lists 38 projects across those six countries: UAE (9), Spain (3), Qatar (2), Oman (14), United Kingdom (2) and Saudi Arabia (8). Prices are not published on the listing page; buyers register interest to get pricing, availability and payment plans.
""")

add(D, "DarGlobal projects in the UAE (Dubai and Ras Al Khaimah)", "https://darglobal.co.uk/projects#uae", """
DarGlobal projects in the United Arab Emirates:
- Trump International Hotel & Tower Dubai, Dubai: https://darglobal.co.uk/trump-international-hotel-and-tower-dubai
- D-Villas at Jumeirah Golf Estates, Dubai: https://darglobal.co.uk/d-villas-at-jge
- The Astera, Interiors by Aston Martin, Al Marjan Island, Ras Al Khaimah: https://darglobal.co.uk/the-astera
- DG1, Dubai: https://darglobal.co.uk/dg1
- Da Vinci Tower, Interiors by Pagani, Dubai: https://darglobal.co.uk/davinci-tower-by-pagani
- Urban Oasis by Missoni, Dubai: https://darglobal.co.uk/urban-oasis-by-missoni
- W Residences, Dubai: https://darglobal.co.uk/w-residences
- The Pagani Penthouse, Dubai: https://darglobal.co.uk/one-of-one/project-pagani
- Top of the Astera, Al Marjan Island, RAK: https://darglobal.co.uk/one-of-one/top-of-the-astera
""")

add(D, "DarGlobal projects in Spain", "https://darglobal.co.uk/projects#spain", """
DarGlobal projects in Spain:
- Tierra Viva, design inspired by Automobili Lamborghini, Benahavís: https://darglobal.co.uk/tierra-viva
- Painite Villas, design inspired by Automobili Lamborghini, Benahavís: https://darglobal.co.uk/one-of-one/painite-villas-design-inspired-by-Automobili-Lamborghini
- Marea, Interiors by Missoni, Cortesin: https://darglobal.co.uk/marea
""")

add(D, "DarGlobal projects in Qatar", "https://darglobal.co.uk/projects#qatar", """
DarGlobal projects in Qatar:
- Les Vagues by Elie Saab, Doha: https://darglobal.co.uk/les-vagues
- Trump International Simaisma, Qatar (Trump villas within Trump International Golf Club Simaisma; sales opened Oct 2026 per DarGlobal press): https://darglobal.co.uk/lp/trump-international-qatar
- L'Horizon (by Elie Saab), Doha, is also linked from DarGlobal project pages as another project: https://darglobal.co.uk/lhorizon-by-eliesaab
""")

add(D, "DarGlobal projects in Oman (AIDA, Muscat)", "https://darglobal.co.uk/landing-page/aida", """
AIDA is DarGlobal's Oman masterplan, described on its homepage as one of the world's largest premium mixed-use developments. Projects in Oman listed by DarGlobal (Muscat / AIDA):
- Aida (masterplan): https://darglobal.co.uk/landing-page/aida
- Trump International Hotel, Oman: https://darglobal.co.uk/aida-trump-international-hotel
- Trump Cliff Villas: https://darglobal.co.uk/aida-trump-international-cliff-villas
- Trump Golf Villas: https://darglobal.co.uk/aida-trump-villas
- Fairway Villas: https://darglobal.co.uk/fairway-villas-aida-oman
- Azure Oceanfront Villas, interiors by Fendi Casa: https://darglobal.co.uk/one-of-one/fendi-casa-azure-oceanfront-villas
- Amour Sans Detour: https://darglobal.co.uk/amour-sans-detour
- Amour Sans Detour 2: https://darglobal.co.uk/amour-sans-detour-2
- The Great Escape: https://darglobal.co.uk/the-great-escape-1-aida-oman
- The Great Escape 2: https://darglobal.co.uk/the-great-escape-2-aida-oman
- Coastal Investment Villas: https://darglobal.co.uk/aida-coastal-investment-villas
- Sunrise Haven: https://darglobal.co.uk/Sunrise-Haven-Luxury-Villas
- Marriott Residences Aida: https://darglobal.co.uk/marriott-residences-aida-oman
- Nickelodeon Hotels & Resorts, AIDA: https://darglobal.co.uk/play-project/nickelodeon
""")

add(D, "DarGlobal projects in the United Kingdom (London)", "https://darglobal.co.uk/projects#uk", """
DarGlobal projects in the United Kingdom:
- The Mulliner, 149 Old Park Lane, London: https://darglobal.co.uk/the-mulliner
- 7&8 Albert Hall Mansions, overlooking Hyde Park, London: https://darglobal.co.uk/one-of-one/THE-ALBERT-HALL-MANSION
""")

add(D, "DarGlobal projects in Saudi Arabia (Jeddah and Riyadh)", "https://darglobal.co.uk/projects#saudi", """
DarGlobal projects in Saudi Arabia:
- Trump Tower Jeddah, Jeddah Corniche: https://darglobal.co.uk/trump-tower-jeddah
- Trump Park Residences, Amaya, Jeddah: https://darglobal.co.uk/trump-plaza/park-residences
- Trump Executive Residences, Amaya, Jeddah (premium furnished Trump residences): https://darglobal.co.uk/trump-plaza/executive-residences
- Amaya, Jeddah (luxury plots): https://darglobal.co.uk/amaya/amaya-plots
- Padel Living Residences, Jeddah: https://darglobal.co.uk/amaya/padel-living
- Trump Mansions, Rayana, Wadi Safar, Riyadh (Trump-branded residences): https://darglobal.co.uk/rayana/trump-mansions
- DarGlobal Mansions, interiors by Fendi Casa, Wadi Safar, Riyadh: https://darglobal.co.uk/rayana/darglobal-mansions-fendi-casa
- Neptune, interiors by Mouawad, Riyadh: https://darglobal.co.uk/neptune
""")

add(D, "Trump International Hotel & Tower Dubai", "https://darglobal.co.uk/trump-international-hotel-and-tower-dubai", """
Trump International Hotel & Tower Dubai (Dubai, UAE) – branded hotel & residential tower. Status: under development. Unit types: 1, 2, 3 bedroom apartments and 4 bedroom duplex penthouses. Area 764–7,720 sq ft (109–722 sqm). Featuring the highest pool in the world. Every unit has sea or Burj Khalifa views. Handover scheduled December 2031. DarGlobal is master developer.
It combines three elements in one address on Sheikh Zayed Road at the gateway to Downtown Dubai: a five-star Trump International hotel, The Trump members-only club (annual fee; residents get priority access; includes signature bar, cigar lounge, golf simulator, spa treatment rooms, meeting rooms, dedicated pool) and the Trump Residences. It is described as the first and only Trump-branded development in the Middle East.
Resident amenities: rooftop infinity pool (highest in the world), state-of-the-art gym, owners lounge, kids play area.
Price and payment plan: not published on the page; the sales team confirms current unit availability, pricing and payment plan on request. Buyers can register interest, download the brochure or book a private viewing at darglobal.co.uk. The page advises buyers to seek independent investment advice.
""")

add(D, "The Astera, Interiors by Aston Martin (Al Marjan Island, RAK)", "https://darglobal.co.uk/the-astera", """
The Astera, Interiors by Aston Martin – Al Marjan Island, Ras Al Khaimah (RAK), UAE. Property type: beach residences and villas. Status: under development. Units: 1 to 3 bedroom residences and 3 bedroom beach villas. Area 682–12,277 sq ft (61–265 sqm). Handover scheduled December 2028. Aston Martin's design team did the interiors of every residence. Direct beach access.
Amenities: direct beach access, premium 24/7 security, fitness center, spa, infinity pool, sauna, pool bar, indoor cinema, yoga lawn, multipurpose hall, kids play area.
Why invest (as stated by DarGlobal): 10-year Golden Visa with an investment of AED 2 million; 0% income tax and 0% property tax; about 5 minutes from the planned Wynn Resort; about 60 minutes from Dubai International Airport; 100% business ownership; potential yields beyond 9%; average apartment capital values up about 35% in the last year; projected 3–3.5 million tourists by 2030; RERA and escrow buyer protection; branded residences price premiums of 30%–200%. The page advises independent investment advice.
Price and payment plan: not published; contact the sales team. Related: Top of the Astera (https://darglobal.co.uk/one-of-one/top-of-the-astera).
""")

add(D, "Trump Tower Jeddah", "https://darglobal.co.uk/trump-tower-jeddah", """
Trump Tower Jeddah – seafront residences on the Jeddah Corniche, Saudi Arabia. 47 floors. Unit types: 1, 2, 3, 4 bedroom apartments and 3, 4 bedroom penthouses. Area 70–365 sqm. Completion scheduled December 2029. Red Sea views; near the marina, the Formula 1 street circuit and King Fahd Fountain.
Features & amenities: uninterrupted sea views, prime Corniche location, Trump Private Club, 24/7 concierge, meeting rooms, cigar lounge, fine dining, pool, kids pool, jacuzzi, gym, yoga zone. An online residence navigator lets buyers choose a residence.
Why invest in Saudi Arabia (as stated): 30-year corporate tax exemption; investing SAR 4 million unlocks premium Saudi residency; 0% income tax and capital gains tax; investors can open a Saudi bank account on a visit visa; infrastructure growth; host of Expo 2030 and the 2034 World Cup; SAR pegged to the US dollar.
Disclaimer on page: Trump Tower Jeddah is owned and developed by DarGlobal Holdings Real Estate, which uses the Trump name under licence; it is not owned, developed or sold by The Trump Organization.
Price and payment plan: not published; the sales team confirms pricing and payment terms.
""")

# ---------------- Wasalt ----------------
add(W, "Wasalt – platform overview (English homepage)", "https://wasalt.sa/en", """
Wasalt is a Saudi-based, AI-backed real estate platform for verified properties, projects, masterplans, online auctions and daily rentals. It connects buyers, renters, developers and brokers across Saudi Arabia, aiming to make property search simpler, more transparent and data-driven.
Homepage sections: Buy, Rent, Projects, Daily Rentals and Barter (new); city selection; apartments for sale in Riyadh, Jeddah, Makkah and Madinah; "Find your next real estate investment – discover verified projects"; connect with brokers by sharing your requirements; participation in Infath and private auctions covering real estate, vehicles and movable assets; Wasalt and Wasalt Business apps; and guidance for landlords and brokers on listing properties, including daily rentals with weekly earnings.
Licensing: Wasalt is a REGA licensed platform (Real Estate General Authority) and is shown as a Ministry of Tourism licensed platform. Wasalt Auctions sell real estate through timed auctions.
Pricing: individual listing prices appear on each listing; the homepage publishes no single price.
""")

add(W, "Wasalt – corporate / PropTech services", "https://wasalt.sa/en/corporate", """
Wasalt Real Estate Services describes itself as a leading PropTech company with an AI-powered real estate portal for verified properties, projects, masterplans and online auctions. Products: Wasalt Search (AI-powered platform for verified properties), Wasalt Auctions (online and hybrid real estate auctions), AI-driven insights and price trends, and direct connection with brokers. Figures shown: 400K+ and 295K+ monthly active users. License No. 1200016591. Property-for-sale pages exist for Riyadh, Jeddah, Makkah, Dammam, Al Khobar, Khamis Mushayt and Egypt.
""")

add(W, "Wasalt – properties for rent in Saudi Arabia", "https://wasalt.sa/en/properties-for-rent-in-saudi-arabia", """
Wasalt's rentals page lists apartments and villas across Saudi Arabia, fully furnished, semi-furnished or unfurnished, with filters. Listings show type, area in SQM, bedrooms, district and city (for example apartments in Al Hammraa, Khobar and West An-Naseem, Riyadh), and an annual rent where stated (one semi-furnished apartment listing shows 42,000 yearly). Listing prices change, so check the live listing.
The page's FAQ says expatriates with a valid Iqama (residency permit) can legally rent homes or commercial units in Saudi Arabia, and that the Ejar platform is commonly used to register lease agreements under Ministry of Housing regulations. It recommends trusted platforms like Wasalt with verified, regularly updated listings to avoid scams and outdated listings.
""")

add(W, "Wasalt – properties for rent in Riyadh", "https://wasalt.sa/en/properties-for-rent-in-riyadh", """
Wasalt's Riyadh rentals page lists furnished and unfurnished apartments and villas with search filters. Example districts: Al-Malqa, Al-Arid, Al-Nuzha and An-Narjis (North Riyadh); Al Bayan, An-Nadheem, East An-Naseem and Al-Muanisiyah (East Riyadh). Listings state type, area, bedrooms and orientation (e.g. villas facing north or west with 3–5 bedrooms; apartments with 1–2 bedrooms). Prices are shown per listing on the live page.
""")

add(W, "Wasalt – company background and products (third-party description)", "https://www.quaraholding.com/en/investments/wasalt", """
Third-party description (Quara Holding): Wasalt was founded in 2020, is licensed by REGA and is a joint venture between Dar Al Arkan (leading Saudi developer with 27+ years of experience) and Quara Holding (technology startup incubator). It cites 500,000+ unique users. Products: Wasalt Properties (search with verified data, prices and nearby amenities), Wasalt Auctions (live real estate auctions), Wasalt Matchmaker (submit requirements and get matched with agents) and Wasalt Projects (book residential units in master-planned communities).
""")

add(W, "Wasalt – mobile app description (third-party store listing)", "https://play.google.com/store/apps/details?id=com.wasalt.app", """
App store description of Wasalt (Wasalt Real Estate Services Company): a platform for searching and advertising real estate for sale or rent in Saudi Arabia, with documented properties in main cities such as Riyadh, Jeddah, Dammam and Al-Khobar, including apartments, villas, lands, projects and plans, plus electronic auctions. Projects: browse exclusive projects from developers and book an apartment, duplex or villa using a bank card. Auctions: create an e-wallet, fund it from your bank account and bid from your phone. Developers and brokers publish via the Wasalt Business app. Contact: info@wasalt.com; address: Building No. 8246, King Abdulaziz Road, Al Wizarat District, Riyadh 12622, Saudi Arabia.
""")

out = pathlib.Path(__file__).with_name("seed_data.json")
out.write_text(json.dumps(docs, ensure_ascii=False, indent=1))
print(len(docs), "documents ->", out)
