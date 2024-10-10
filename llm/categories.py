def category_mapper(category):
    return {
        1: (
            "Adult Products and Services: Products and services intended for adult use, "
            "such as adult entertainment, dating services, and adult novelties."
        ),
        2: (
            "Alcohol: Alcoholic beverages and related products like Alco Pops, "
            "Bars, Beer, Hard Sodas, Seltzers, Spirits, and Wine."
        ),
        3: (
            "Culture and Fine Arts: Museums, galleries, and cultural events "
            "showcasing art and fine arts."
        ),
        4: (
            "Business and Industrial: Advertising, business services, energy, "
            "manufacturing, logistics, and related industries."
        ),
        5: (
            "Cannabis: Cannabis-related products such as consumables, edibles, "
            "CBD products, accessories, and stores."
        ),
        6: (
            "Clothing and Accessories: Clothing for all genders and ages, "
            "sportswear, accessories, footwear, jewelry, and wedding attire."
        ),
        7: (
            "Collectables and Antiques: Collectibles such as antiques, coins, "
            "collectible figures, and sports memorabilia."
        ),
        8: "Computer Software: Software solutions and productivity tools.",
        9: (
            "Cosmetic Services: Beauty services such as skincare, hair removal, "
            "and beauty salons."
        ),
        10: (
            "Consumer Electronics: Phones, computers, cameras, audio equipment, "
            "and other electronic devices."
        ),
        11: (
            "Consumer Packaged Goods: Beverages, cosmetics, frozen foods, snacks, "
            "personal care, household products, and more."
        ),
        12: "Dating: Dating, matchmaking, and online relationship platforms.",
        13: (
            "Debated Sensitive Social Issues: Advertisements related to sensitive "
            "social issues like politics and human rights."
        ),
        14: (
            "Durable Goods: Long-lasting goods like appliances, furniture, "
            "batteries, and household accessories."
        ),
        15: "Dieting and Weightloss: Weight loss products, diet plans, and supplements.",
        16: (
            "Education and Careers: Educational services, career development, "
            "online courses, and certifications."
        ),
        17: (
            "Events and Performances: Public or private events like concerts, "
            "festivals, theater shows, and auctions."
        ),
        18: (
            "Family and Parenting: Products and services for families, childcare, "
            "and parenting resources."
        ),
        19: (
            "Finance and Insurance: Financial services, loans, banking, "
            "insurance, and accounting."
        ),
        20: (
            "Food and Beverage Services: Bakeries, bars, catering services, "
            "and restaurants."
        ),
        21: (
            "Gambling: Gambling services such as casinos, online betting, "
            "lotteries, and contests."
            ),
        22: "Green/Eco: Eco-friendly products, green energy, and sustainability solutions.",
        23: (
            "Gifts and Holiday Items: Holiday-related products like flowers, "
            "gift baskets, and decorations."
            ),
        24: (
            "Health and Medical Services: Health services such as hospitals, "
            "clinics, alternative medicine, and medical services."
            ),
        25: (
            "Home and Garden Services: Home improvement services, "
            "landscaping, and appliance repair."
            ),
        26: "Legal Services: Lawyers, bail bonds, and legal support services.",
        27: "Media: TV, radio, magazines, blogs, forums, and social networks.",
        28: (
            "Metals: Precious metals and related services, including gold, "
            "silver, and coin exchanges."
            ),
        29: (
            "Non-Fiat Currency: Cryptocurrency, digital assets, and "
            "cryptocurrency exchanges."
            ),
        30: "Non-Profits: Charitable organizations, donations, and civic organizations.",
        31: (
            "Pet Ownership: Pet adoption, care services, pet food, supplies, "
            "and veterinary care."
        ),
        32: (
            "Personal/Consumer Telecom: Telecommunication services, including "
            "mobile services, home internet, and wireless networks."
            ),
        33: (
            "Pharmaceuticals: Products related to the pharmaceutical industry, "
            "including over-the-counter and prescription medications."
            ),
        34: "Politics: Political ads, campaigns, elections, and ballot measures.",
        35: (
            "Real Estate: Real estate services and property listings, both "
            "residential and commercial."
        ),
        36: (
            "Religion and Spirituality: Religious services, spiritual "
            "practices, astrology, and prayer groups."
            ),
        37: (
            "Retail: Retail goods like clothing, groceries, electronics, "
            "arts and crafts, and sporting goods."
            ),
        38: (
            "Fitness Activities: Fitness-related services such as gyms, "
            "personal training, yoga studios, and dance studios."
            ),
        39: (
            "Sexual Health: Products and services related to sexual "
            "health, such as contraceptives and sexual health clinics."
            ),
        40: (
            "Sporting Goods: Sports equipment, fitness gear, indoor "
            "and outdoor recreational products."
            ),
        41: (
            "Travel and Tourism: Travel-related services like "
            "accommodations, flights, cruises, vacation rentals, and travel planning."
            ),
        42: (
            "Tobacco: Tobacco products such as cigarettes, cigars, "
            "smokeless tobacco, and vaping products."
            ),
        43: (
            "Vehicles: Vehicle services and products like car dealerships, "
            "auto repair, parts, electric and hybrid vehicles."
        ),
        44: (
            "Weapons and Ammunition: Firearms, ammunition, gun "
            "accessories, and non-projectile weapons."
            ),
        0: (
            "No category applies or its impossible to determine "
            "the category with the information providades."
        ),
    }[category]
