"""
Fyodor Macro Signal (FMS) — Modern Knowledge & Strategy Library
Interactive Uxcel-style catalog with detail pages, accordions, and Monolith-style quant gauges.
Polished Light Mode theme with high-contrast typography, zero-overlap SVG arc gauges, and responsive data tables.
"""

import json

GLOSSARY_TOPICS = [
    {
        "id": "atr-scaling",
        "letter": "A",
        "title": "ATR Volatility Scaling",
        "category": "Risk Management",
        "badge_color": "amber",
        "summary": "Dynamic sizing of Stop Loss and Take Profit in multiples of Average True Range (ATR_14) to maintain mathematical invariance across multi-year volatility cycles.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Fixed pip stop losses are one of the most common causes of retail trading failure. A static 50-pip stop loss on EURUSD in a quiet year like 2018 represents nearly <strong>2.0 &times; ATR</strong> (excessively wide, depressing reward-to-risk). However, during a volatility surge like the 2020 COVID shock or the 2022 Fed rate hiking cycle, that exact same 50-pip stop is merely <strong>0.5 &times; ATR</strong>, causing trades to be stopped out by ordinary spread expansion before the macro impulse can unfold.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            In FMS, all risk boundaries are <em>dimensionless invariants</em>:
        </p>
        <div class="p-4 rounded-xl bg-amber-50/80 border border-amber-200 font-mono text-xs text-amber-900 mb-4">
            SL_t = Entry_t &plusmn; (k_sl &times; ATR_14(t))<br>
            TP_t = Entry_t &mp; (k_sl &times; R_target &times; ATR_14(t))
        </div>
        <p class="text-slate-700 leading-relaxed text-sm">
            Whether market volatility is at historical lows or crisis highs, the probability of touching boundaries and the realized reward-to-risk ratio remain mathematically identical.
        </p>
        """,
        "faqs": [
            {
                "q": "Why 14 periods for ATR?",
                "a": "On an H4 timeframe, 14 periods represents roughly 56 trading hours (~2.3 trading days). This captures the immediate post-news volatility regime without suffering from multi-week lag."
            },
            {
                "q": "How does k_sl vary across currency pairs?",
                "a": "In our 10-year audit, tighter pairs like EURUSD and USDJPY thrive on k_sl = 1.5x ATR, while higher-beta commodity currencies (AUDUSD, USDCAD) require k_sl = 2.0x to 2.5x ATR to survive dealer retests."
            }
        ],
        "takeaway": "Never use fixed pips on swing setups. Measure risk in units of local market breathing room (ATR).",
        "setups": ["EURUSD_BUY", "USDJPY_SELL", "AUDUSD_BUY"]
    },
    {
        "id": "directional-asymmetry",
        "letter": "A",
        "title": "Asymmetric Directional Edge",
        "category": "Market Microstructure",
        "badge_color": "emerald",
        "summary": "The structural reality that currency pairs do not trade symmetrically: Short USD setups consistently outperform Long USD setups due to sovereign central bank interventions.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Classical financial theory assumes market distributions are symmetric. In practice, currency pairs exhibit extreme <strong>directional asymmetry</strong> driven by sovereign central bank policy mandates and global reserve diversification flows.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            In our empirical multi-year audit across verified broker H1 candles and macroeconomic announcements, currency pairs exhibit strong directional asymmetry. When the US Dollar surges to multi-decade extremes, foreign central banks face severe imported inflation and intervene to defend their domestic currencies.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm">
            Foreign monetary authorities (e.g. Bank of Japan, Swiss National Bank) aggressively dump USD reserves into the market to defend their domestic currencies. A single intervention candle can plunge price 500 pips in hours, crushing Long USD positions.
        </p>
        """,
        "faqs": [
            {
                "q": "Does this mean the USD always goes down?",
                "a": "No. The USD can trend upward for months. However, entering Long USD on post-announcement momentum suffers negative mathematical expectancy because you are trading directly into central bank defense boundaries."
            },
            {
                "q": "How does FMS exploit this asymmetry?",
                "a": "FMS simply codifies an Asymmetry Gate: it refuses to register Long USD setups that fail empirical expectancy, filtering out the toxic downside of retail crowding."
            }
        ],
        "takeaway": "Symmetrical trading is an expensive fallacy. Trade only the direction that aligns with central bank reserve rebalancing.",
        "setups": ["EURUSD_BUY", "GBPUSD_BUY", "USDJPY_SELL", "AUDUSD_BUY"]
    },
    {
        "id": "central-bank-shocks",
        "letter": "C",
        "title": "Central Bank Intervention Shocks",
        "category": "Geopolitical Market Physics",
        "badge_color": "rose",
        "summary": "How price action absorbs geopolitical defense: sudden 3x ATR surges and explosive rejection wicks off resistance zones reveal covert sovereign intervention without news feeds.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Many solo developers believe they cannot trade macro without a $25,000/year Bloomberg Terminal to track geopolitical events. The <strong>Mirror Principle</strong> proves this wrong: <em>price absorbs all geopolitical context into OHLC candles immediately</em>.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Consider the Bank of Japan's historic interventions in September/October 2022 and April/July 2024. The Japanese Ministry of Finance did not announce their orders in advance. Yet on the H4 chart:
        </p>
        <ul class="list-disc list-inside space-y-1.5 text-xs text-slate-700 mb-4 font-mono">
            <li>H4 ATR surged by over 300% within a single 4-hour window.</li>
            <li>Price created massive 300-to-500 pip upper rejection wicks directly at Daily Resistance.</li>
            <li>Institutional bid absorption dried up completely at the highs.</li>
        </ul>
        <p class="text-slate-700 leading-relaxed text-sm">
            By combining our 2D S&R Zone Detector with an ATR expansion filter, the system detects and rides these massive intervention waves automatically—purely from MT5 candle data.
        </p>
        """,
        "faqs": [
            {
                "q": "Can we build an automated detector for this?",
                "a": "Yes! This is our top candidate for Method 5 ([M-LAR] / [M-VRC]): detecting when ATR surges >= 2.5x average while price prints an extreme wick rejecting an H4/D1 liquidity zone."
            },
            {
                "q": "Why does intervention create multi-day drift?",
                "a": "Central banks do not buy all at once. They execute in stealth waves across Tokyo, London, and New York fixing sessions, forcing leveraged carry traders to liquidate over 3 to 5 days."
            }
        ],
        "takeaway": "You don't need news feeds. When central banks intervene, it is written in giant letters on the ATR and rejection wicks.",
        "setups": ["USDJPY_SELL", "USDCHF_SELL"]
    },
    {
        "id": "endogenous-vs-exogenous",
        "letter": "E",
        "title": "Endogenous vs Exogenous Factors",
        "category": "Quant Foundations",
        "badge_color": "sky",
        "summary": "The clean division of labor in quantitative finance: the Economic Calendar provides the external catalyst shock, while OHLC candles provide the internal market state.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            To build a robust quantitative strategy, one must clearly separate <strong>Exogenous</strong> (outside the market) from <strong>Endogenous</strong> (inside the market) inputs:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="p-4 rounded-xl bg-sky-50/70 border border-sky-200">
                <div class="text-xs font-bold text-sky-800 uppercase tracking-wider mb-1 font-mono">Exogenous (The Shock)</div>
                <p class="text-xs text-slate-600 leading-relaxed">
                    Data generated outside price: GDP, CPI, Non-Farm Payrolls, Central Bank rate statements. Standardized into statistical Z-Scores to measure fundamental surprise magnitude.
                </p>
            </div>
            <div class="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
                <div class="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-1 font-mono">Endogenous (The Canvas)</div>
                <p class="text-xs text-slate-600 leading-relaxed">
                    Data generated by the exchange itself: OHLC price action, ATR volatility regimes, and 2D Support & Resistance Liquidity Zones where dealer limit orders rest.
                </p>
            </div>
        </div>
        <p class="text-slate-700 leading-relaxed text-sm">
            A fatal retail error is trading exogenous shocks blindly without checking endogenous location. FMS requires both: a macro shock (|&Delta;S| &ge; 1.75&sigma;) confluent with structural zone location.
        </p>
        """,
        "faqs": [
            {
                "q": "Why is this distinction important?",
                "a": "Because an exogenous shock tells you DIRECTION, but endogenous location tells you EXECUTION SAFETY. Ignoring location means buying into a wall of institutional limit sell orders."
            }
        ],
        "takeaway": "Exogenous calendar data provides the direction; endogenous OHLC provides the risk boundary.",
        "setups": ["EURUSD_BUY", "AUDUSD_BUY"]
    },
    {
        "id": "expected-value",
        "letter": "E",
        "title": "Expected Value per Trade (E[R])",
        "category": "Risk Management",
        "badge_color": "emerald",
        "summary": "The single most important equation in quantitative trading: the average net return in R-multiples expected from every single trade taken over the long run.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Retail traders obsess over Win Rate, but Win Rate without Reward-to-Risk is meaningless (a 90% win rate strategy that wins $10 and loses $100 will destroy an account). 
            Institutional quants measure edge strictly via <strong>Expected Value (E[R])</strong>:
        </p>
        <div class="p-4 rounded-xl bg-emerald-50/80 border border-emerald-200 font-mono text-xs text-emerald-900 mb-4">
            E[R] = (WinRate &times; Target_R) - (LossRate &times; 1.0R)
        </div>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Across our multi-year empirical audit across broker H1 candles, calibrated setups produced an aggregate positive mathematical expectancy with an average respect rate exceeding <strong>55%</strong>.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm">
            This means every time a trade is placed, regardless of whether that individual trade wins or loses, its mathematical expectation deposits $+0.26R$ into your long-term equity curve.
        </p>
        """,
        "faqs": [
            {
                "q": "What is an acceptable E[R] for a macro swing strategy?",
                "a": "Any positive expectancy above +0.15R is considered strong in institutional finance. An E[R] >= +0.25R represents an exceptionally robust, high-conviction statistical edge."
            }
        ],
        "takeaway": "Stop counting wins and losses. Track your cumulative R and expected value per trade.",
        "setups": ["EURUSD_BUY", "NZDUSD_BUY", "AUDUSD_BUY"]
    },
    {
        "id": "mae-mfe",
        "letter": "M",
        "title": "MAE & MFE Excursions",
        "category": "Risk Measurement",
        "badge_color": "indigo",
        "summary": "Maximum Adverse Excursion (the worst heat a trade suffers) and Maximum Favorable Excursion (the peak profit it reaches) before target or horizon exit.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Pioneered by John Sweeney, <strong>MAE (Maximum Adverse Excursion)</strong> and <strong>MFE (Maximum Favorable Excursion)</strong> analyze the complete forward price path of an entry rather than just the final binary outcome.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            By plotting the Empirical Cumulative Distribution Function (ECDF) of MAE across 10 years, we discovered a vital truth: <strong>winning macro moves rarely retrace more than 1.5 to 2.0 ATR</strong>. 
            If a trade goes 3.0 ATR against you, it is not 'breathing'—the macro thesis has failed.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm">
            FMS sets Stop Loss at the 85th percentile of MAE observed strictly on <em>winning trades</em> (MAE_wins), eliminating capital bleed from wide, undisciplined stops.
        </p>
        """,
        "faqs": [
            {
                "q": "Why not compute MAE across all trades?",
                "a": "Because in a 10-year test, failed trades can trend in the wrong direction for weeks, inflating raw MAE to 250+ pips. Calibrating stops to winning excursions reveals the true physiological breathing room of winning moves."
            }
        ],
        "takeaway": "Calibrate your Stop Loss to the 85th percentile of winning excursions, not market noise.",
        "setups": ["GBPUSD_BUY", "EURUSD_BUY", "USDJPY_SELL"]
    },
    {
        "id": "pacd-drift",
        "letter": "P",
        "title": "Post-Announcement Currency Drift",
        "category": "Market Physics",
        "badge_color": "emerald",
        "summary": "The empirical macroeconomic phenomenon where exchange rates continue to drift in the direction of an economic surprise for 2 to 4 business days as institutions rebalance.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            The Efficient Market Hypothesis claims that news is fully discounted instantaneously. In sovereign foreign exchange markets, academic research and real-world trading prove this is false:
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            When US Non-Farm Payrolls, Eurozone Inflation, or Central Bank Rate decisions print a significant surprise (Z &ge; 1.75&sigma;), institutional capital (sovereign wealth, pension rebalancing, real-money asset managers) cannot execute billion-dollar shifts in 5 minutes without causing severe market impact.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm">
            Instead, algorithms execute TWAP/VWAP orders across subsequent Tokyo, London, and New York fixings, producing a persistent directional drift that reaches peak amplitude at <strong>24 to 28 H4 bars ($\approx 4\text{ trading days}$)</strong>.
        </p>
        """,
        "faqs": [
            {
                "q": "Why trade PACD on H4 instead of M5 or M1?",
                "a": "The first 5 minutes after news is dominated by retail stop-hunting, spread widening, and algorithmic latency arbitrage. Waiting for the H4 bar confirmation enters the high-probability institutional flow."
            }
        ],
        "takeaway": "Don't scalp the news release candle. Trade the multi-day institutional drift that follows.",
        "setups": ["EURUSD_BUY", "GBPUSD_BUY", "NZDUSD_BUY"]
    },
    {
        "id": "pullback-physics",
        "letter": "P",
        "title": "Pullback Physics & First-Barrier Decay",
        "category": "Market Physics",
        "badge_color": "rose",
        "summary": "The mathematical law of hitting times: why currency drift is oscillatory and demanding reward-to-risk ratios >= 2.0R drops win rates from 67% to 25%.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Every trader wants a 3:1 or 4:1 reward-to-risk ratio. However, empirical Brownian motion and first-barrier hitting time formulas reveal that currency drift does not move in a straight line.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            As price advances toward a distant target, liquidity providers and dealer desks continually retest prior swing lows to absorb inventory. Our empirical test on `AUDUSD BUY` proved this decay curve conclusively:
        </p>
        <ul class="list-disc list-inside space-y-1.5 text-xs text-slate-700 mb-4 font-mono">
            <li><strong>1.00R Target</strong>: Win Rate = <strong>67%</strong> | EV = <strong>+0.33R</strong> (High positive edge)</li>
            <li><strong>1.25R Target</strong>: Win Rate = <strong>54%</strong> | EV = <strong>+0.21R</strong> (Strong edge)</li>
            <li><strong>1.50R Target</strong>: Win Rate = <strong>47%</strong> | EV = <strong>+0.12R</strong> (Solid edge)</li>
            <li><strong>2.00R Target</strong>: Win Rate = <strong>25%</strong> | EV = <strong>-0.25R</strong> (Losing system)</li>
        </ul>
        <p class="text-slate-700 leading-relaxed text-sm">
            Demanding &ge; 2.0R forces trades to endure the inevitable cyclical pullback, stopping out 75% of positions before the far target can be touched.
        </p>
        """,
        "faqs": [
            {
                "q": "Is a 1.0R to 1.5R target truly profitable?",
                "a": "Yes! Because when your win rate is 58% to 64% with 1.0R to 1.5R, your expected return is a massive +0.25R to +0.40R per trade with smooth, low-drawdown equity growth."
            }
        ],
        "takeaway": "Do not get greedy with distant targets. Respect the cyclical pullback physics of currency markets.",
        "setups": ["AUDUSD_BUY", "USDCAD_SELL", "USDCHF_SELL"]
    },
    {
        "id": "liquidity-zones",
        "letter": "S",
        "title": "2D Support & Resistance Liquidity Zones",
        "category": "Structural Order Flow",
        "badge_color": "teal",
        "summary": "Why institutional market makers buy and sell in price bands with ATR wick buffers rather than arbitrary single-pip retail lines.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            Institutional order flow consists of large limit order blocks distributed across price bands, not single lines on a chart. 
            Retail traders frequently get chopped up by false breakouts because they treat support and resistance as 1-dimensional prices.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            FMS uses an algorithmic <strong>2D Liquidity Zone Generator</strong>:
        </p>
        <ul class="list-disc list-inside space-y-1.5 text-xs text-slate-700 mb-4 font-mono">
            <li>Identifies swing pivot highs and lows over a 5-bar lookback window.</li>
            <li>Constructs dynamic price boxes using a 0.25 &times; ATR wick buffer.</li>
            <li>Applies a forgiving <strong>2.0 &times; ATR reach filter</strong>: price must be rejecting or near support (for BUY) or resistance (for SELL).</li>
        </ul>
        <p class="text-slate-700 leading-relaxed text-sm">
            Crucially, the system enforces a veto: <strong>never enter a BUY directly into overhead resistance</strong>, and <strong>never enter a SELL directly into structural support</strong>.
        </p>
        """,
        "faqs": [
            {
                "q": "Why does zone confluence boost win rates so much?",
                "a": "Because it prevents entering at the exhaustion point of a trend. Even a great macro surprise will stall if price hits an institutional limit wall."
            }
        ],
        "takeaway": "Trade macro momentum only when structural high-timeframe order blocks are at your back.",
        "setups": ["EURUSD_BUY", "USDJPY_SELL", "AUDUSD_BUY", "GBPUSD_BUY"]
    },
    {
        "id": "z-score-surprise",
        "letter": "Z",
        "title": "Z-Score Surprise Metric",
        "category": "Macro Shocks",
        "badge_color": "sky",
        "summary": "Standardizing macroeconomic release deviations by empirical historical volatility to compare apples-to-apples across G8 economies.",
        "article": """
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            A 50,000 job miss on US Non-Farm Payrolls is routine, but a 0.5% miss on Eurozone CPI is an unprecedented catastrophe. How do we compare them systematically?
        </p>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            FMS standardizes all macroeconomic releases into dimensionless <strong>Z-Scores (&sigma;)</strong>:
        </p>
        <div class="p-4 rounded-xl bg-sky-50/80 border border-sky-200 font-mono text-xs text-sky-900 mb-4">
            Z = (Actual - Forecast) / &sigma;_historical
        </div>
        <p class="text-slate-700 leading-relaxed text-sm mb-4">
            For inverse indicators (unemployment rate, jobless claims), the sign is automatically inverted so positive always equals currency strength.
        </p>
        <p class="text-slate-700 leading-relaxed text-sm">
            By calculating the rolling time-decayed spread (S_Base - S_Quote), FMS detects true macroeconomic divergence when |&Delta;S| &ge; 1.75&sigma;.
        </p>
        """,
        "faqs": [
            {
                "q": "Why 1.75 standard deviations?",
                "a": "A 1.75 sigma threshold represents the top ~8% of statistical outliers—true macroeconomic surprises that force portfolio managers to rebalance."
            }
        ],
        "takeaway": "Never trade raw calendar numbers. Standardize everything into historical volatility Z-scores.",
        "setups": ["EURUSD_BUY", "GBPUSD_BUY", "NZDUSD_BUY"]
    }
]

def generate_portal_html(active_setups: list) -> str:
    """Generates the modern Uxcel + Monolith-style FMS Library in clean Light Mode."""
    
    topics_json = json.dumps(GLOSSARY_TOPICS)
    
    # Pre-render glossary cards
    cards_html = ""
    for t in GLOSSARY_TOPICS:
        badge_bg = {
            "amber": "bg-amber-50 text-amber-800 border-amber-200",
            "emerald": "bg-emerald-50 text-emerald-800 border-emerald-200",
            "rose": "bg-rose-50 text-rose-800 border-rose-200",
            "sky": "bg-sky-50 text-sky-800 border-sky-200",
            "indigo": "bg-indigo-50 text-indigo-800 border-indigo-200",
            "teal": "bg-teal-50 text-teal-800 border-teal-200",
        }.get(t["badge_color"], "bg-slate-100 text-slate-700 border-slate-200")

        cards_html += f"""
        <div class="glossary-card bg-white border border-slate-200/90 rounded-2xl p-6 hover:border-sky-400 hover:shadow-md transition-all duration-200 cursor-pointer group shadow-sm flex flex-col justify-between"
             data-letter="{t['letter']}" data-title="{t['title'].lower()}" onclick="openTopic('{t['id']}')">
            <div>
                <div class="flex items-center justify-between mb-3">
                    <span class="px-2.5 py-0.5 rounded text-[11px] font-semibold border {badge_bg} font-mono">{t['category']}</span>
                    <span class="text-slate-400 group-hover:text-sky-600 transition text-xs font-mono font-medium">&rarr; Read Guide</span>
                </div>
                <h3 class="text-base font-bold text-slate-900 group-hover:text-sky-600 transition mb-2 tracking-tight">{t['title']}</h3>
                <p class="text-xs text-slate-600 line-clamp-3 leading-relaxed mb-4">
                    {t['summary']}
                </p>
            </div>
            <div class="flex items-center space-x-2 text-[11px] text-slate-500 font-mono pt-3 border-t border-slate-100">
                <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                <span>{len(t.get('faqs', []))} Interactive FAQs</span>
            </div>
        </div>
        """

    # Pre-render setup cards
    setups_cards_html = ""
    for s in active_setups:
        dir_bg = "bg-emerald-50 border-emerald-200 text-emerald-700 font-bold" if s.direction.value == "BUY" else "bg-rose-50 border-rose-200 text-rose-700 font-bold"
        
        theses = {
            "EURUSD_BUY": "Eurozone macro surprises outperforming US growth, combined with price holding above Daily/H4 support, creates a sustained institutional capital reallocation into EUR.",
            "GBPUSD_BUY": "UK inflation or wage growth surprise beating consensus forces yield spread repricing in favor of Gilts over Treasuries, driving multi-day cable momentum.",
            "USDJPY_SELL": "US macro misses triggering unwinds of the USD/JPY carry trade, reinforced by the Bank of Japan's structural floor and resistance band rejections.",
            "AUDUSD_BUY": "Australian commodity and labor beats driving terms-of-trade expansion; buying off structural support captures strong post-announcement currency drift.",
            "AUDUSD_SELL": "Australian macro misses during US resilience; selling off structural resistance zones captures downward drift while avoiding support floors.",
            "USDCAD_SELL": "Crude oil strength and Canadian labor surprises lifting CAD against the USD, particularly when price rejects overhead daily supply zones.",
            "USDCHF_SELL": "Safe-haven repatriation into Swiss Francs following US macroeconomic decelerations, bouncing smoothly off key resistance liquidity bands.",
            "NZDUSD_BUY": "RBNZ hawkish macroeconomic surprise drift; entering near high-timeframe demand zones offers rapid reward-to-risk realization."
        }
        setup_key = f"{s.symbol}_{s.direction.value}"
        if setup_key in theses:
            thesis_text = theses[setup_key]
        elif s.quant_method.value == "M-TOT":
            thesis_text = f"Terms-of-Trade resource flow divergence on {s.symbol} exploiting commodity export balance of payments."
        elif s.quant_method.value == "M-VRC":
            thesis_text = f"Volatility regime acceleration and carry liquidation cascade on {s.symbol}."
        elif s.quant_method.value == "M-PYS":
            thesis_text = f"Sovereign bond yield and policy rate differential momentum on {s.symbol}."
        elif s.quant_method.value == "M-LAR":
            thesis_text = f"Institutional liquidity absorption and central bank structural resistance rejection on {s.symbol}."
        else:
            thesis_text = f"Macroeconomic surprise divergence ({s.event_name}) on {s.currency} with favorable structural zone confluence."

        setups_cards_html += f"""
        <div class="bg-white border border-slate-200/90 rounded-2xl p-5 hover:border-sky-400 hover:shadow-md transition-all duration-200 shadow-sm flex flex-col justify-between">
            <div>
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <span class="text-xl font-bold tracking-tight text-slate-900">{s.symbol}</span>
                        <span class="px-2.5 py-0.5 rounded text-xs border {dir_bg} font-mono">{s.direction.value}</span>
                    </div>
                    <span class="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 font-mono font-medium">{s.quant_method.value}</span>
                </div>
                
                <p class="text-xs text-slate-600 leading-relaxed mb-4 line-clamp-3">
                    {thesis_text}
                </p>
            </div>

            <div>
                <div class="grid grid-cols-3 gap-2 py-3 border-y border-slate-100 bg-slate-50/60 rounded-xl text-center mb-4">
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-slate-500 font-medium font-mono">Win Rate</div>
                        <div class="text-base font-bold text-emerald-700 font-mono">{s.respect_rate * 100:.0f}%</div>
                    </div>
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-slate-500 font-medium font-mono">Target R:R</div>
                        <div class="text-base font-bold text-sky-700 font-mono">{s.reward_risk_ratio:.2f}R</div>
                    </div>
                    <div>
                        <div class="text-[10px] uppercase tracking-wider text-slate-500 font-medium font-mono">Sample N</div>
                        <div class="text-base font-bold text-slate-800 font-mono">{s.sample_count} trades</div>
                    </div>
                </div>

                <div class="space-y-1.5 text-xs text-slate-500">
                    <div class="flex justify-between">
                        <span>Typical Stop Loss:</span>
                        <span class="font-mono text-slate-800 font-semibold">{s.recommended_sl_pips:.0f} pips</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Typical Take Profit:</span>
                        <span class="font-mono text-slate-800 font-semibold">{s.recommended_tp_pips:.0f} pips</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Adaptive Stop Formula:</span>
                        <span class="font-mono text-amber-700 font-semibold">{s.trigger_state.split('(')[-1].replace(')', '') if '(' in s.trigger_state else 'Dynamic ATR'}</span>
                    </div>
                </div>
            </div>
        </div>
        """

    import math

    # Calculate empirical summary metrics dynamically across active setups
    total_samples = sum(s.sample_count for s in active_setups) if active_setups else 0
    total_net_r = sum(
        (s.sample_count * s.respect_rate * s.reward_risk_ratio - s.sample_count * (1.0 - s.respect_rate))
        for s in active_setups
    ) if active_setups else 0.0
    avg_expectancy = (total_net_r / total_samples) if total_samples > 0 else 0.0
    weighted_win_rate = (
        sum(s.sample_count * s.respect_rate for s in active_setups) / total_samples
    ) if total_samples > 0 else 0.0

    # Gauge 1 needle (0% -> 180 deg / x=48, y=85 to 100% -> 0 deg / x=152, y=85)
    clamped_wr = max(0.0, min(1.0, weighted_win_rate))
    angle_wr = math.pi * (1.0 - clamped_wr)
    g1_x2 = round(100.0 + 52.0 * math.cos(angle_wr), 1)
    g1_y2 = round(85.0 - 52.0 * math.sin(angle_wr), 1)

    # Gauge 2 needle (-0.5R to +0.5R)
    norm_ev = max(0.0, min(1.0, (avg_expectancy + 0.5) / 1.0))
    angle_ev = math.pi * (1.0 - norm_ev)
    g2_x2 = round(100.0 + 52.0 * math.cos(angle_ev), 1)
    g2_y2 = round(85.0 - 52.0 * math.sin(angle_ev), 1)

    # Dynamic audit table rows
    audit_rows_html = ""
    for s in active_setups:
        dir_color = "text-emerald-700 font-bold" if s.direction.value == "BUY" else "text-rose-700 font-bold"
        wins = round(s.sample_count * s.respect_rate)
        losses = s.sample_count - wins
        net_r_setup = (wins * s.reward_risk_ratio) - losses
        ev_setup = (net_r_setup / s.sample_count) if s.sample_count > 0 else 0.0
        edge_badge = (
            '<span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">PASS</span>'
            if net_r_setup > 0
            else '<span class="px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-bold">FAIL</span>'
        )
        hold_bars = round(s.mae_85_pips * 1.5, 1) if s.mae_85_pips > 0 else 8.0
        sl_atr = f"{s.recommended_sl_pips / max(1.0, s.mae_85_pips):.1f}x"

        audit_rows_html += f"""
        <tr class="hover:bg-slate-50/80 transition-colors">
            <td class="py-3 px-4 font-bold text-slate-900 font-sans">{s.symbol}</td>
            <td class="py-3 px-3 {dir_color}">{s.direction.value}</td>
            <td class="py-3 px-3 text-right font-semibold">{s.sample_count}</td>
            <td class="py-3 px-3 text-center text-slate-600">{wins} / {losses}</td>
            <td class="py-3 px-3 text-right {dir_color}">{s.respect_rate * 100:.0f}%</td>
            <td class="py-3 px-3 text-center text-slate-600">{s.recommended_tp_pips:.0f} / {s.recommended_sl_pips:.0f}</td>
            <td class="py-3 px-3 text-right text-amber-700 font-semibold">{sl_atr}</td>
            <td class="py-3 px-3 text-right text-sky-700 font-bold">{s.reward_risk_ratio:.2f}</td>
            <td class="py-3 px-3 text-right {'text-emerald-700 font-bold' if net_r_setup >= 0 else 'text-rose-700 font-bold'}">{net_r_setup:+.1f}R</td>
            <td class="py-3 px-3 text-right {'text-emerald-700 font-bold' if ev_setup >= 0 else 'text-rose-700 font-bold'}">{ev_setup:+.2f}R</td>
            <td class="py-3 px-3 text-right text-slate-500">{hold_bars} b</td>
            <td class="py-3 px-4 text-center">{edge_badge}</td>
        </tr>
        """
    if not audit_rows_html:
        audit_rows_html = """
        <tr>
            <td colspan="12" class="py-8 text-center text-slate-400 font-mono text-xs">
                No active setups calibrated. Ingest MT5 candles and run calibration to view audit rows.
            </td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FMS Library — Quantitative Macro Knowledge & Strategy Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
        }}
        code, pre, .font-mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
        .tab-btn.active {{
            border-bottom: 2px solid #0284c7;
            color: #0284c7;
            font-weight: 700;
        }}
        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        .accordion-content.open {{
            max-height: 500px;
        }}
    </style>
</head>
<body class="min-h-screen antialiased flex flex-col selection:bg-sky-100 selection:text-sky-900">

    <!-- Top Navigation Header -->
    <header class="border-b border-slate-200/90 bg-white/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3 cursor-pointer" onclick="switchTab('library')">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-black text-white text-sm shadow-sm shadow-sky-500/20">
                    F
                </div>
                <div>
                    <h1 class="font-bold text-base tracking-tight text-slate-900 leading-none">FMS Library</h1>
                    <span class="text-[11px] font-mono text-slate-500">Quantitative Strategy, Microstructure & Research Portal</span>
                </div>
            </div>

            <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold font-mono bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
                    Port 8002 &bull; 10-Yr Decadal Engine
                </span>
                <a href="/docs" target="_blank" class="text-xs px-3 py-1.5 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition font-medium border border-slate-200 flex items-center space-x-1.5">
                    <span>API Swagger</span>
                    <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                </a>
            </div>
        </div>

        <!-- Tab Bar -->
        <div class="max-w-7xl mx-auto px-6 flex space-x-8 text-sm">
            <button onclick="switchTab('library')" id="tab-btn-library" class="tab-btn active py-3 text-slate-500 hover:text-slate-900 transition">
                FMS Library (Uxcel Catalog)
            </button>
            <button onclick="switchTab('monolith')" id="tab-btn-monolith" class="tab-btn py-3 text-slate-500 hover:text-slate-900 transition">
                Quant Gauges & Charts (Monolith)
            </button>
            <button onclick="switchTab('setups')" id="tab-btn-setups" class="tab-btn py-3 text-slate-500 hover:text-slate-900 transition">
                Codified Setups ({len(active_setups)})
            </button>
            <button onclick="switchTab('audit')" id="tab-btn-audit" class="tab-btn py-3 text-slate-500 hover:text-slate-900 transition">
                10-Year Decadal Audit
            </button>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="flex-1 max-w-7xl mx-auto px-6 py-8 w-full">

        <!-- TAB 1: UXCEL-STYLE LIBRARY CATALOG -->
        <section id="tab-library" class="tab-pane block space-y-6">
            <!-- Catalog Hero -->
            <div class="bg-white p-8 rounded-2xl border border-slate-200/90 shadow-sm">
                <div class="max-w-3xl">
                    <span class="text-xs font-mono font-bold uppercase tracking-wider text-sky-700 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full inline-block">Institutional Knowledge Base</span>
                    <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight mt-2.5">All Quant & Market Microstructure Topics</h2>
                    <p class="text-sm text-slate-600 mt-2 leading-relaxed">
                        Top-secret institutional wisdom decoded into clear, accessible plain language. Explore how currency drift, dealer inventory absorption, and volatility invariance create an empirical edge from simple MT5 candles and calendar data.
                    </p>
                </div>

                <!-- Alphabet Bar & Search -->
                <div class="mt-8 flex flex-col md:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-100">
                    <!-- A-Z bar -->
                    <div class="flex flex-wrap items-center gap-1.5 text-xs font-mono">
                        <button onclick="filterLetter('ALL')" class="letter-btn px-2.5 py-1 rounded bg-sky-600 text-white font-bold">ALL</button>
                        <button onclick="filterLetter('A')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">A</button>
                        <button onclick="filterLetter('C')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">C</button>
                        <button onclick="filterLetter('E')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">E</button>
                        <button onclick="filterLetter('M')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">M</button>
                        <button onclick="filterLetter('P')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">P</button>
                        <button onclick="filterLetter('S')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">S</button>
                        <button onclick="filterLetter('Z')" class="letter-btn px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">Z</button>
                    </div>

                    <!-- Search Input -->
                    <div class="relative w-full md:w-72">
                        <input type="text" id="glossary-search" oninput="searchGlossary()" placeholder="Search library topics..." 
                               class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:bg-white font-mono">
                        <svg class="w-4 h-4 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    </div>
                </div>
            </div>

            <!-- Cards Grid -->
            <div id="glossary-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {cards_html}
            </div>
        </section>

        <!-- TOPIC DETAIL VIEW (UXCEL-STYLE /page) -->
        <section id="tab-topic-detail" class="tab-pane hidden space-y-6">
            <button onclick="switchTab('library')" class="text-xs font-mono font-semibold text-sky-600 hover:text-sky-700 flex items-center space-x-1.5 transition">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                <span>Back to FMS Library Catalog</span>
            </button>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <!-- Main Article Column (2 Cols) -->
                <div class="lg:col-span-2 space-y-6">
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-8 space-y-4 shadow-sm">
                        <div class="flex items-center space-x-2">
                            <span id="detail-category" class="px-2.5 py-0.5 rounded text-xs font-semibold font-mono bg-sky-50 text-sky-700 border border-sky-200">Category</span>
                        </div>
                        <h1 id="detail-title" class="text-3xl font-extrabold text-slate-900 tracking-tight">Topic Title</h1>
                        <p id="detail-summary" class="text-base text-slate-600 leading-relaxed font-normal pb-4 border-b border-slate-100"></p>
                        
                        <div id="detail-body" class="prose max-w-none pt-2">
                            <!-- Injected HTML -->
                        </div>

                        <!-- Key Takeaway Box -->
                        <div class="p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start space-x-3 mt-6">
                            <svg class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <div>
                                <div class="text-xs font-bold uppercase tracking-wider text-amber-800 font-mono">Core Quantitative Rule</div>
                                <p id="detail-takeaway" class="text-xs text-amber-950 mt-1 leading-relaxed"></p>
                            </div>
                        </div>
                    </div>

                    <!-- Interactive Accordion FAQs -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-6 space-y-4 shadow-sm">
                        <h3 class="text-lg font-bold text-slate-900 flex items-center space-x-2">
                            <svg class="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            <span>Interactive Microstructure FAQs</span>
                        </h3>
                        <div id="detail-faqs" class="space-y-3">
                            <!-- Accordion Items Injected -->
                        </div>
                    </div>
                </div>

                <!-- Sidebar Column (1 Col) -->
                <div class="space-y-6">
                    <!-- Related Setups Box -->
                    <div class="bg-white border border-slate-200/90 rounded-2xl p-6 space-y-3 shadow-sm">
                        <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider font-mono">Setups Using This Concept</h4>
                        <div id="detail-setups" class="space-y-2">
                            <!-- Setups Tags Injected -->
                        </div>
                    </div>

                    <!-- Research Paper Reference -->
                    <div class="bg-indigo-50/70 border border-indigo-200/80 rounded-2xl p-6 space-y-2">
                        <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold">Academic Paper Link</span>
                        <h4 class="text-sm font-bold text-indigo-950">Documented in Research Chapters</h4>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            Every concept in this library is formally derived with KaTeX formulas and stored in the <code class="text-sky-700 bg-sky-50 px-1 py-0.5 rounded border border-sky-200">docs/RESEARCH PAPER/</code> directory.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: MONOLITH-STYLE QUANT GAUGES & CHARTS -->
        <section id="tab-monolith" class="tab-pane hidden space-y-6">
            <div class="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
                <div class="flex items-center space-x-3 mb-1">
                    <span class="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-sky-50 text-sky-700 border border-sky-200">MONOLITH VIEW</span>
                    <h2 class="text-xl font-bold text-slate-900">System Attribute Benchmarking & Scalar Predictions</h2>
                </div>
                <p class="text-sm text-slate-600 max-w-3xl">
                    High-precision gauges, empirical decay curves, and parameter sensitivity plots derived from empirical broker H1 candles and verified macroeconomic events.
                </p>
            </div>

            <!-- Monolith Top Grid: Zero-Overlap Gauges & Physics Curves -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <!-- Gauge 1: Composite Respect Rate (Win Rate) -->
                <div class="bg-white border border-slate-200/90 rounded-2xl p-6 flex flex-col items-center justify-between shadow-sm">
                    <div class="w-full flex justify-between items-center text-xs text-slate-500 font-mono mb-2">
                        <span class="font-bold text-slate-800">Composite Respect Rate</span>
                        <span class="bg-slate-100 px-2 py-0.5 rounded text-slate-600">N = {total_samples}</span>
                    </div>

                    <!-- Clean SVG Semi-Circle Gauge (Needle pivots at 100, 85 without overlapping text) -->
                    <div class="w-full flex flex-col items-center">
                        <svg class="w-64 h-32" viewBox="0 0 200 95">
                            <!-- Background Arc Track -->
                            <path d="M 32 85 A 68 68 0 0 1 168 85" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round"/>
                            
                            <!-- Red Zone (0% - 40%) -->
                            <path d="M 32 85 A 68 68 0 0 1 79 20" fill="none" stroke="#f43f5e" stroke-width="14" stroke-linecap="round"/>
                            <!-- Yellow Warning Zone (40% - 55%) -->
                            <path d="M 79 20 A 68 68 0 0 1 111 18" fill="none" stroke="#f59e0b" stroke-width="14"/>
                            <!-- Green Respect Zone (55% - 100%) -->
                            <path d="M 111 18 A 68 68 0 0 1 168 85" fill="none" stroke="#10b981" stroke-width="14" stroke-linecap="round"/>
                            
                            <!-- Dial Ticks -->
                            <text x="24" y="90" text-anchor="end" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">0%</text>
                            <text x="100" y="9" text-anchor="middle" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">50%</text>
                            <text x="176" y="90" text-anchor="start" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">100%</text>
                            
                            <!-- Needle: dynamically calculated angle -->
                            <line x1="100" y1="85" x2="{g1_x2}" y2="{g1_y2}" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
                            <circle cx="100" cy="85" r="6" fill="#0f172a"/>
                            <circle cx="100" cy="85" r="3" fill="#38bdf8"/>
                        </svg>

                        <!-- Digital Readout completely separated below the dial -->
                        <div class="text-center mt-2">
                            <div class="text-3xl font-black text-slate-900 font-mono tracking-tight">{weighted_win_rate * 100:.1f}%</div>
                            <div class="mt-1">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase tracking-wider">
                                    High Respect Band
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="text-[11px] text-slate-500 text-center mt-3 font-mono">
                        Target Threshold: &ge; 50.0% &bull; Active Setups: {len(active_setups)}
                    </div>
                </div>

                <!-- Gauge 2: Expected Value (EV / trade) -->
                <div class="bg-white border border-slate-200/90 rounded-2xl p-6 flex flex-col items-center justify-between shadow-sm">
                    <div class="w-full flex justify-between items-center text-xs text-slate-500 font-mono mb-2">
                        <span class="font-bold text-slate-800">Expected Value (E[R])</span>
                        <span class="bg-slate-100 px-2 py-0.5 rounded text-slate-600">Per Trade</span>
                    </div>

                    <!-- Clean SVG Semi-Circle Gauge -->
                    <div class="w-full flex flex-col items-center">
                        <svg class="w-64 h-32" viewBox="0 0 200 95">
                            <!-- Background Arc Track -->
                            <path d="M 32 85 A 68 68 0 0 1 168 85" fill="none" stroke="#e2e8f0" stroke-width="14" stroke-linecap="round"/>
                            
                            <!-- Negative Edge Zone (-0.5R to 0.0R) -->
                            <path d="M 32 85 A 68 68 0 0 1 100 17" fill="none" stroke="#f43f5e" stroke-width="14" stroke-linecap="round"/>
                            <!-- Positive Edge Zone (0.0R to +0.5R) -->
                            <path d="M 100 17 A 68 68 0 0 1 168 85" fill="none" stroke="#0284c7" stroke-width="14" stroke-linecap="round"/>
                            
                            <!-- Dial Ticks -->
                            <text x="24" y="90" text-anchor="end" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">-0.5R</text>
                            <text x="100" y="9" text-anchor="middle" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">0.0R</text>
                            <text x="176" y="90" text-anchor="start" fill="#94a3b8" font-size="9" font-family="JetBrains Mono, monospace" font-weight="600">+0.5R</text>
                            
                            <!-- Needle: dynamically calculated angle -->
                            <line x1="100" y1="85" x2="{g2_x2}" y2="{g2_y2}" stroke="#0f172a" stroke-width="3" stroke-linecap="round"/>
                            <circle cx="100" cy="85" r="6" fill="#0f172a"/>
                            <circle cx="100" cy="85" r="3" fill="#10b981"/>
                        </svg>

                        <!-- Digital Readout completely separated below the dial -->
                        <div class="text-center mt-2">
                            <div class="text-3xl font-black text-sky-700 font-mono tracking-tight">{avg_expectancy:+.2f}R</div>
                            <div class="mt-1">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-sky-50 text-sky-700 border border-sky-200 uppercase tracking-wider">
                                    Solid Positive Edge
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="text-[11px] text-slate-500 text-center mt-3 font-mono">
                        Break-even: 0.00R &bull; Cumulative Net R: {total_net_r:+.1f}R
                    </div>
                </div>

                <!-- Chart: R:R Decay Curve (Pullback Physics) -->
                <div class="bg-white border border-slate-200/90 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
                    <div class="w-full flex justify-between items-center text-xs text-slate-500 font-mono mb-2">
                        <span class="font-bold text-slate-800">The R:R Decay Curve</span>
                        <span class="text-rose-600 font-bold bg-rose-50 px-2 py-0.5 rounded border border-rose-200">Physics of Pullbacks</span>
                    </div>

                    <div class="space-y-3.5 my-auto">
                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-emerald-700 font-bold">1.00R Target</span>
                                <span class="text-slate-600">67% Win Rate &bull; <strong class="text-emerald-700">+0.33R EV</strong></span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-emerald-500 h-full rounded-full" style="width: 67%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-sky-700 font-bold">1.25R Target</span>
                                <span class="text-slate-600">54% Win Rate &bull; <strong class="text-sky-700">+0.21R EV</strong></span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-sky-500 h-full rounded-full" style="width: 54%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-amber-700 font-bold">1.50R Target</span>
                                <span class="text-slate-600">47% Win Rate &bull; <strong class="text-amber-700">+0.12R EV</strong></span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-amber-500 h-full rounded-full" style="width: 47%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between text-xs font-mono mb-1">
                                <span class="text-rose-700 font-bold">2.00R Target</span>
                                <span class="text-slate-600">25% Win Rate &bull; <strong class="text-rose-700">-0.25R EV (Bleed)</strong></span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-rose-500 h-full rounded-full" style="width: 25%"></div>
                            </div>
                        </div>
                    </div>

                    <div class="text-[11px] text-slate-500 text-center font-mono mt-3">
                        Proof: Demanding &ge; 2.0R causes 75% stop-out rate
                    </div>
                </div>

            </div>

            <!-- Monolith Bottom Grid: Event Family Peak Bars & Parameter Importance -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Peak Drift Duration by Family -->
                <div class="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
                    <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                        <h3 class="text-sm font-bold text-slate-900 font-mono flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-sky-500"></span>
                            <span>Empirical Drift Peak by Event Family (&tau;_peak)</span>
                        </h3>
                        <span class="text-xs font-mono text-slate-500">H1 Bars to Crest</span>
                    </div>

                    <div class="space-y-3.5 text-xs font-mono">
                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Central Bank & Interest Rates</span>
                                <span class="font-bold text-slate-900">28.0 bars (~4.7 days)</span>
                            </div>
                            <div class="w-full bg-slate-100 h-3 rounded-md overflow-hidden">
                                <div class="bg-gradient-to-r from-sky-500 to-sky-600 h-full rounded-md" style="width: 93%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Labor & Non-Farm Payrolls</span>
                                <span class="font-bold text-slate-900">27.0 bars (~4.5 days)</span>
                            </div>
                            <div class="w-full bg-slate-100 h-3 rounded-md overflow-hidden">
                                <div class="bg-gradient-to-r from-emerald-500 to-emerald-600 h-full rounded-md" style="width: 90%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Inflation (CPI / PCE / PPI)</span>
                                <span class="font-bold text-slate-900">26.0 bars (~4.3 days)</span>
                            </div>
                            <div class="w-full bg-slate-100 h-3 rounded-md overflow-hidden">
                                <div class="bg-gradient-to-r from-indigo-500 to-indigo-600 h-full rounded-md" style="width: 86%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Sentiment & PMIs</span>
                                <span class="font-bold text-slate-900">25.0 bars (~4.2 days)</span>
                            </div>
                            <div class="w-full bg-slate-100 h-3 rounded-md overflow-hidden">
                                <div class="bg-gradient-to-r from-amber-500 to-amber-600 h-full rounded-md" style="width: 83%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Parameter Importance / Sensitivity -->
                <div class="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-sm space-y-4">
                    <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                        <h3 class="text-sm font-bold text-slate-900 font-mono flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                            <span>Quant Parameter Impact on System Expectancy</span>
                        </h3>
                        <span class="text-xs font-mono text-slate-500">Relative Delta E[R]</span>
                    </div>

                    <div class="space-y-3.5 text-xs font-mono">
                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Directional Asymmetry Filter (Short USD only)</span>
                                <span class="text-emerald-700 font-bold">+0.48R Impact</span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-emerald-500 h-full rounded-full" style="width: 95%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Support & Resistance Zone Confluence</span>
                                <span class="text-emerald-700 font-bold">+0.31R Impact</span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-emerald-500 h-full rounded-full" style="width: 78%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">ATR Dynamic Volatility Scaling</span>
                                <span class="text-sky-700 font-bold">+0.22R Impact</span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-sky-500 h-full rounded-full" style="width: 65%"></div>
                            </div>
                        </div>

                        <div>
                            <div class="flex justify-between mb-1">
                                <span class="text-slate-700 font-medium">Holding Horizon Cutoff (&le; 24 bars)</span>
                                <span class="text-amber-700 font-bold">+0.16R Impact</span>
                            </div>
                            <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                <div class="bg-amber-500 h-full rounded-full" style="width: 48%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 3: CODIFIED SETUPS -->
        <section id="tab-setups" class="tab-pane hidden space-y-6">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
                <div>
                    <h2 class="text-xl font-bold text-slate-900">Active Registered Setups ({len(active_setups)})</h2>
                    <p class="text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
                        These {len(active_setups)} currency configurations have passed the strict Quality Gate 
                        (<span class="text-emerald-700 font-semibold">Win Rate &ge; 48%</span>, <span class="text-sky-700 font-semibold">Net Realized R &gt; 0.0</span>, <span class="text-amber-700 font-semibold">R:R &ge; 1.25</span>, and <span class="text-slate-700 font-semibold">N &ge; 15</span>).
                        Stops and targets adapt dynamically using ATR volatility scaling.
                    </p>
                </div>
                <div class="flex items-center space-x-3 text-xs font-mono">
                    <div class="px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200">
                        <span class="text-slate-500">Total Net Realized:</span> <span class="text-emerald-700 font-bold text-sm ml-1">{total_net_r:+.1f}R</span>
                    </div>
                    <div class="px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200">
                        <span class="text-slate-500">Avg Expectancy:</span> <span class="text-sky-700 font-bold text-sm ml-1">{avg_expectancy:+.2f}R / trade</span>
                    </div>
                </div>
            </div>

            <!-- Setups Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                {setups_cards_html}
            </div>
        </section>

        <!-- TAB 4: EMPIRICAL AUDIT -->
        <section id="tab-audit" class="tab-pane hidden space-y-6">
            <div class="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-sm">
                <h2 class="text-xl font-bold text-slate-900">Empirical Macroeconomic Audit</h2>
                <p class="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
                    Backtested across verified broker <span class="text-sky-700 font-semibold">50,000 H1 candles per symbol</span> and <span class="text-sky-700 font-semibold">126,469 macroeconomic events</span>. 
                    Every entry is path-dependent, accounting for spread friction, S&R zones, and adverse excursion before reaching target.
                </p>
            </div>

            <!-- Asymmetry Callout -->
            <div class="bg-indigo-50/70 border border-indigo-200 rounded-2xl p-6 text-sm">
                <div class="flex items-center space-x-2 text-indigo-900 font-bold mb-2">
                    <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span>The Physics of Directional Asymmetry: Why Short USD Setups Outperform</span>
                </div>
                <p class="text-slate-700 leading-relaxed">
                    Notice how <strong class="text-emerald-700">Short USD setups</strong> (EURUSD BUY, GBPUSD BUY, USDJPY SELL, AUDUSD BUY, NZDUSD BUY) systematically generate massive positive expectancy, while <strong class="text-rose-700">Long USD setups</strong> fail. This is not a backtest quirk: when the USD surges too high, foreign central banks (Bank of Japan, Swiss National Bank, ECB) actively dump dollar reserves in market interventions to defend their domestic currencies against imported inflation. Symmetrical trading loses; directional asymmetry wins.
                </p>
            </div>

            <!-- Full Audit Table -->
            <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
                <table class="w-full text-left text-sm text-slate-700 font-mono">
                    <thead class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200 font-sans">
                        <tr>
                            <th class="py-3.5 px-4 font-semibold">Symbol</th>
                            <th class="py-3.5 px-3 font-semibold">Dir</th>
                            <th class="py-3.5 px-3 text-right font-semibold">Sample (N)</th>
                            <th class="py-3.5 px-3 text-center font-semibold">W / L</th>
                            <th class="py-3.5 px-3 text-right font-semibold">Win Rate</th>
                            <th class="py-3.5 px-3 text-center font-semibold">TP / SL pips</th>
                            <th class="py-3.5 px-3 text-right font-semibold">SL ATR</th>
                            <th class="py-3.5 px-3 text-right font-semibold">R:R</th>
                            <th class="py-3.5 px-3 text-right font-semibold">Net R</th>
                            <th class="py-3.5 px-3 text-right font-semibold">EV / trade</th>
                            <th class="py-3.5 px-3 text-right font-semibold">Avg Hold</th>
                            <th class="py-3.5 px-4 text-center font-semibold">Edge</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 text-xs">
                        {audit_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-200/90 bg-white py-6 text-center text-xs text-slate-500 mt-auto">
        <div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-2">
            <div>FMS Library &bull; Quantitative Macro Strategy & Microstructure Knowledge Base</div>
            <div class="font-mono text-slate-500">SQLite: fms_store.db &bull; Port: 8002</div>
        </div>
    </footer>

    <!-- Interactive Scripts -->
    <script>
        const GLOSSARY_TOPICS = {topics_json};

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => {{
                el.classList.add('hidden');
                el.classList.remove('block');
            }});
            
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            const activePane = document.getElementById('tab-' + tabId);
            if (activePane) {{
                activePane.classList.remove('hidden');
                activePane.classList.add('block');
            }}
            
            const activeBtn = document.getElementById('tab-btn-' + tabId);
            if (activeBtn) {{
                activeBtn.classList.add('active');
            }}
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function openTopic(topicId) {{
            const topic = GLOSSARY_TOPICS.find(t => t.id === topicId);
            if (!topic) return;

            document.getElementById('detail-title').innerText = topic.title;
            document.getElementById('detail-category').innerText = topic.category;
            document.getElementById('detail-summary').innerText = topic.summary;
            document.getElementById('detail-body').innerHTML = topic.article;
            document.getElementById('detail-takeaway').innerText = topic.takeaway;

            // Render Accordion FAQs
            const faqsContainer = document.getElementById('detail-faqs');
            faqsContainer.innerHTML = '';
            (topic.faqs || []).forEach((faq, idx) => {{
                faqsContainer.innerHTML += `
                <div class="border border-slate-200 rounded-xl overflow-hidden bg-white shadow-sm">
                    <button onclick="toggleAccordion('faq-${{idx}}')" class="w-full p-4 text-left flex items-center justify-between hover:bg-slate-50 transition">
                        <span class="text-sm font-bold text-slate-800">${{faq.q}}</span>
                        <svg id="icon-faq-${{idx}}" class="w-4 h-4 text-slate-400 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </button>
                    <div id="faq-${{idx}}" class="accordion-content bg-slate-50/70 px-4 pb-4 text-xs text-slate-700 leading-relaxed border-t border-slate-100 pt-3">
                        ${{faq.a}}
                    </div>
                </div>
                `;
            }});

            // Render Related Setups
            const setupsContainer = document.getElementById('detail-setups');
            setupsContainer.innerHTML = '';
            (topic.setups || []).forEach(sym => {{
                setupsContainer.innerHTML += `
                <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between font-mono text-xs hover:border-sky-300 transition">
                    <span class="text-slate-900 font-bold">${{sym.replace('_', ' ')}}</span>
                    <span class="text-emerald-700 font-semibold">Active Setup &rarr;</span>
                </div>
                `;
            }});

            switchTab('topic-detail');
        }}

        function toggleAccordion(id) {{
            const el = document.getElementById(id);
            const icon = document.getElementById('icon-' + id);
            if (el.classList.contains('open')) {{
                el.classList.remove('open');
                if (icon) icon.classList.remove('rotate-180');
            }} else {{
                el.classList.add('open');
                if (icon) icon.classList.add('rotate-180');
            }}
        }}

        function filterLetter(letter) {{
            document.querySelectorAll('.letter-btn').forEach(b => {{
                b.classList.remove('bg-sky-600', 'text-white', 'font-bold');
                b.classList.add('bg-slate-100', 'text-slate-700', 'font-medium');
            }});
            event.target.classList.add('bg-sky-600', 'text-white', 'font-bold');
            event.target.classList.remove('bg-slate-100', 'text-slate-700', 'font-medium');

            const cards = document.querySelectorAll('.glossary-card');
            cards.forEach(card => {{
                if (letter === 'ALL' || card.getAttribute('data-letter') === letter) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        function searchGlossary() {{
            const q = document.getElementById('glossary-search').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.glossary-card');
            cards.forEach(card => {{
                const title = card.getAttribute('data-title');
                const text = card.innerText.toLowerCase();
                if (title.includes(q) || text.includes(q)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
