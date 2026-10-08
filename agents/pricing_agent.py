import re
import statistics

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None


# ============================================================
# REFERENCE PRICE RANGES
# ============================================================

FALLBACK_PRICES = {

    "bumper": (16000, 24000),

    "headlight": (6500, 10000),

    "fender": (6000, 12000),

    "bonnet": (7000, 12000),

    "hood": (7000, 12000),

    "grille": (2500, 6000),

    "door": (10000, 18000),

    "mirror": (3000, 7000),

    "windshield": (5000, 10000),

    "radiator": (7000, 14000),

    "condenser": (7000, 14000),

    "suspension": (8000, 16000),

    "steering": (7000, 15000),

    "tail light": (3000, 7000),

    "taillight": (3000, 7000),

    "boot": (8000, 14000),

    "quarter panel": (9000, 18000),

    "wheel": (5000, 12000),

    "tyre": (3500, 9000),

    "airbag": (15000, 35000),

    "sensor": (3000, 10000),

    "camera": (5000, 15000),

}


# ============================================================
# VEHICLE PRICE MULTIPLIERS
# ============================================================

PREMIUM_BRANDS = [

    "bmw",

    "mercedes",

    "mercedes-benz",

    "audi",

    "volvo",

    "jaguar",

    "lexus",

    "porsche",

    "land rover",

    "land rover",

]


UPPER_MID_BRANDS = [

    "jeep",

    "mini",

    "skoda",

    "volkswagen",

    "toyota",

]


# ============================================================
# VEHICLE MULTIPLIER
# ============================================================

def get_vehicle_multiplier(
    vehicle_name
):

    vehicle = str(
        vehicle_name or ""
    ).lower()


    if any(
        brand in vehicle
        for brand in PREMIUM_BRANDS
    ):

        return 1.70


    if any(
        brand in vehicle
        for brand in UPPER_MID_BRANDS
    ):

        return 1.30


    return 1.00


# ============================================================
# PART NAME NORMALIZATION
# ============================================================

def normalize_part_name(
    part
):

    if part is None:

        return "Unknown component"


    return str(
        part
    ).strip()


# ============================================================
# FALLBACK PART PRICE
# ============================================================

def find_fallback_price(
    part
):

    part_lower = (
        normalize_part_name(
            part
        ).lower()
    )


    for keyword, price_range in (
        FALLBACK_PRICES.items()
    ):

        if keyword in part_lower:

            return price_range


    # Generic component fallback

    return (
        5000,
        12000
    )


# ============================================================
# FALLBACK ESTIMATE
# ============================================================

def get_fallback_estimate(
    part,
    action,
    severity,
    vehicle_name
):

    low, high = (
        find_fallback_price(
            part
        )
    )


    multiplier = (
        get_vehicle_multiplier(
            vehicle_name
        )
    )


    low *= multiplier
    high *= multiplier


    action_text = str(
        action or ""
    ).upper()


    severity_text = str(
        severity or ""
    ).upper()


    # --------------------------------------------------------
    # INSPECTION ONLY
    # --------------------------------------------------------

    if "INSPECT" in action_text:

        low *= 0.65
        high *= 0.85


    # --------------------------------------------------------
    # SEVERITY ADJUSTMENT
    # --------------------------------------------------------

    if severity_text == "SEVERE":

        low *= 1.05
        high *= 1.10


    elif severity_text == "HIGH":

        low *= 1.02
        high *= 1.06


    # --------------------------------------------------------
    # CONTROL THE RANGE
    #
    # Maximum difference = ₹10,000
    # --------------------------------------------------------

    midpoint = (
        low + high
    ) / 2


    spread = min(

        10000,

        max(
            2000,
            midpoint * 0.20
        )

    )


    low = (
        midpoint
        - spread / 2
    )


    high = (
        midpoint
        + spread / 2
    )


    low = int(
        round(
            low / 500
        )
        * 500
    )


    high = int(
        round(
            high / 500
        )
        * 500
    )


    if high < low:

        high = low


    return {

        "min":
            low,

        "max":
            high,

        "average":
            int(
                round(
                    midpoint / 500
                )
                * 500
            )

    }


# ============================================================
# EXTRACT INR PRICES
# ============================================================

def extract_prices(
    text
):

    if not text:

        return []


    patterns = [

        r"₹\s?([\d,]+(?:\.\d+)?)",

        r"Rs\.?\s?([\d,]+(?:\.\d+)?)",

        r"INR\s?([\d,]+(?:\.\d+)?)",

    ]


    values = []


    for pattern in patterns:

        matches = re.findall(

            pattern,

            text,

            flags=re.IGNORECASE

        )


        for match in matches:

            try:

                value = float(
                    match.replace(
                        ",",
                        ""
                    )
                )

            except ValueError:

                continue


            # ------------------------------------------------
            # Ignore years
            # ------------------------------------------------

            if (
                1900
                <= value
                <= 2035
            ):

                continue


            # ------------------------------------------------
            # Ignore unrealistic prices
            # ------------------------------------------------

            if value < 500:

                continue


            if value > 500000:

                continue


            values.append(
                value
            )


    return values


# ============================================================
# REMOVE PRICE OUTLIERS
# ============================================================

def filter_price_outliers(
    prices
):

    if not prices:

        return []


    prices = sorted(
        prices
    )


    # Very small sample
    if len(prices) <= 2:

        return prices


    median = statistics.median(
        prices
    )


    lower_limit = (
        median * 0.65
    )


    upper_limit = (
        median * 1.35
    )


    filtered = [

        price

        for price in prices

        if (
            lower_limit
            <= price
            <= upper_limit
        )

    ]


    # If filtering removed everything,
    # keep the median.

    if not filtered:

        return [
            median
        ]


    return filtered


# ============================================================
# CREATE TIGHT MARKET RANGE
# ============================================================

def create_tight_market_range(
    prices
):

    if not prices:

        return None


    filtered = (
        filter_price_outliers(
            prices
        )
    )


    if not filtered:

        return None


    median = statistics.median(
        filtered
    )


    # --------------------------------------------------------
    # Default controlled spread
    # --------------------------------------------------------

    spread = min(

        10000,

        max(
            2000,
            median * 0.20
        )

    )


    low = (
        median
        - spread / 2
    )


    high = (
        median
        + spread / 2
    )


    # --------------------------------------------------------
    # If enough observations exist, use quartiles as an
    # additional sanity check.
    # --------------------------------------------------------

    if len(filtered) >= 4:

        try:

            quartiles = (
                statistics.quantiles(
                    filtered,
                    n=4
                )
            )


            q1 = quartiles[0]

            q3 = quartiles[2]


            low = max(
                low,
                q1
            )


            high = min(
                high,
                q3
            )

        except (
            statistics.StatisticsError
        ):

            pass


    # --------------------------------------------------------
    # Never allow the range to become too narrow or invalid
    # --------------------------------------------------------

    if high <= low:

        low = (
            median * 0.90
        )

        high = (
            median * 1.10
        )


    # --------------------------------------------------------
    # HARD ₹10,000 LIMIT
    # --------------------------------------------------------

    if (
        high - low
        > 10000
    ):

        low = (
            median - 5000
        )

        high = (
            median + 5000
        )


    low = int(
        round(
            low / 500
        )
        * 500
    )


    high = int(
        round(
            high / 500
        )
        * 500
    )


    average = int(
        round(
            median / 500
        )
        * 500
    )


    if high < low:

        high = low


    return {

        "min":
            low,

        "max":
            high,

        "average":
            average

    }


# ============================================================
# SEARCH PUBLIC WEB
# ============================================================

def search_part(
    vehicle_name,
    part
):

    if DDGS is None:

        return {

            "status":
                "SEARCH_UNAVAILABLE",

            "prices":
                [],

            "sources":
                []

        }


    vehicle_name = str(
        vehicle_name or ""
    ).strip()


    part = normalize_part_name(
        part
    )


    # --------------------------------------------------------
    # Search queries
    # --------------------------------------------------------

    queries = [

        (
            f'"{vehicle_name}" '
            f'"{part}" '
            f'price India car spare part'
        ),

        (
            f'{vehicle_name} '
            f'{part} '
            f'price India'
        ),

        (
            f'{vehicle_name} '
            f'{part} '
            f'cost India'
        )

    ]


    prices = []

    sources = []


    # --------------------------------------------------------
    # DDGS SEARCH
    # --------------------------------------------------------

    try:

        with DDGS() as ddgs:

            for query in queries:

                try:

                    results = ddgs.text(

                        query,

                        max_results=6

                    )


                    for result in results:

                        title = result.get(
                            "title",
                            ""
                        )


                        body = result.get(
                            "body",
                            ""
                        )


                        href = result.get(
                            "href",
                            ""
                        )


                        combined_text = (

                            f"{title} "
                            f"{body}"

                        )


                        found_prices = (
                            extract_prices(
                                combined_text
                            )
                        )


                        prices.extend(
                            found_prices
                        )


                        if href:

                            sources.append({

                                "title":
                                    title,

                                "url":
                                    href

                            })


                except Exception:

                    # One failed query should not
                    # stop the complete pricing agent.

                    continue


    except Exception:

        return {

            "status":
                "SEARCH_FAILED",

            "prices":
                [],

            "sources":
                []

        }


    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    prices = sorted(
        set(
            prices
        )
    )


    # --------------------------------------------------------
    # No public prices
    # --------------------------------------------------------

    if not prices:

        return {

            "status":
                "NO_PUBLIC_PRICE",

            "prices":
                [],

            "sources":
                sources[:5]

        }


    # --------------------------------------------------------
    # Create controlled range
    # --------------------------------------------------------

    market_range = (
        create_tight_market_range(
            prices
        )
    )


    return {

        "status":
            "FOUND",

        "prices":
            prices,

        "filtered_prices":
            filter_price_outliers(
                prices
            ),

        "market_range":
            market_range,

        "sources":
            sources[:5]

    }


# ============================================================
# MAIN PRICING AGENT
# ============================================================

def search_part_prices(
    vehicle,
    year,
    damaged_parts
):
    """
    Search public automotive pricing for each detected
    damaged component.

    Public prices are used where available.

    If a suitable public price cannot be found,
    a clearly labelled AI/reference estimate is used.
    """


    vehicle = str(
        vehicle or ""
    ).strip()


    year = (
        str(year).strip()
        if year
        else ""
    )


    # --------------------------------------------------------
    # Vehicle display name
    # --------------------------------------------------------

    if year:

        vehicle_display = (
            f"{vehicle} {year}"
        )

    else:

        vehicle_display = vehicle


    parts = []

    public_count = 0

    reference_count = 0

    all_sources = []


    # ========================================================
    # PROCESS EACH DAMAGED COMPONENT
    # ========================================================

    for damage in (
        damaged_parts or []
    ):

        if not isinstance(
            damage,
            dict
        ):

            continue


        part = damage.get(

            "part",

            "Unknown component"

        )


        action = damage.get(

            "recommended_action",

            "INSPECT"

        )


        severity = damage.get(

            "severity",

            "MODERATE"

        )


        # ----------------------------------------------------
        # PUBLIC WEB SEARCH
        # ----------------------------------------------------

        result = search_part(

            vehicle_name=
                vehicle_display,

            part=
                part

        )


        if (

            result.get(
                "status"
            )
            == "FOUND"

            and

            result.get(
                "market_range"
            )

        ):

            market_range = result[
                "market_range"
            ]


            price_min = int(
                market_range[
                    "min"
                ]
            )


            price_max = int(
                market_range[
                    "max"
                ]
            )


            price_average = int(
                market_range[
                    "average"
                ]
            )


            # ------------------------------------------------
            # FINAL SAFETY LIMIT
            # ------------------------------------------------

            if (
                price_max
                - price_min
                > 10000
            ):

                midpoint = (
                    price_min
                    + price_max
                ) / 2


                price_min = int(
                    round(
                        (
                            midpoint
                            - 5000
                        )
                        / 500
                    )
                    * 500
                )


                price_max = int(
                    round(
                        (
                            midpoint
                            + 5000
                        )
                        / 500
                    )
                    * 500
                )


            parts.append({

                "part":
                    part,

                "price_min":
                    price_min,

                "price_max":
                    price_max,

                "price_average":
                    price_average,

                "price_source":
                    "PUBLIC_WEB",

                "status":
                    "FOUND",

                "observed_prices":
                    result.get(
                        "prices",
                        []
                    )

            })


            public_count += 1


            all_sources.extend(

                result.get(
                    "sources",
                    []
                )

            )


        else:

            # ------------------------------------------------
            # REFERENCE ESTIMATE
            # ------------------------------------------------

            fallback = (
                get_fallback_estimate(

                    part=
                        part,

                    action=
                        action,

                    severity=
                        severity,

                    vehicle_name=
                        vehicle_display

                )
            )


            parts.append({

                "part":
                    part,

                "price_min":
                    fallback[
                        "min"
                    ],

                "price_max":
                    fallback[
                        "max"
                    ],

                "price_average":
                    fallback[
                        "average"
                    ],

                "price_source":
                    "AI_REFERENCE_ESTIMATE",

                "status":
                    "ESTIMATED",

                "observed_prices":
                    []

            })


            reference_count += 1


    # ========================================================
    # OVERALL PRICING STATUS
    # ========================================================

    if (
        public_count > 0
        and
        reference_count == 0
    ):

        overall_status = (
            "PUBLIC_WEB"
        )

    elif (
        public_count > 0
        and
        reference_count > 0
    ):

        overall_status = (
            "MIXED"
        )

    else:

        overall_status = (
            "AI_REFERENCE_ESTIMATE"
        )


    # ========================================================
    # REMOVE DUPLICATE SOURCES
    # ========================================================

    unique_sources = []

    seen_urls = set()


    for source in all_sources:

        if not isinstance(
            source,
            dict
        ):

            continue


        url = source.get(
            "url"
        )


        if not url:

            continue


        if url in seen_urls:

            continue


        seen_urls.add(
            url
        )


        unique_sources.append({

            "title":
                source.get(
                    "title",
                    ""
                ),

            "url":
                url

        })


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "status":
            overall_status,

        "parts":
            parts,

        "public_web_count":
            public_count,

        "reference_estimate_count":
            reference_count,

        "sources":
            unique_sources[:20],

        "message": (

            "Public automotive market prices were used "
            "where suitable listings were available. "
            "Extreme price outliers were filtered. "
            "Unavailable components use clearly labelled "
            "reference estimates. The displayed component "
            "price range is controlled to a maximum "
            "₹10,000 spread."

        )

    }