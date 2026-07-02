"""
DataFactory — generates realistic synthetic records for Saudi/GCC companies.

All figures are plausible but entirely fictional.
Swap individual methods with real API calls when integrating Bloomberg/Tadawul/CapIQ.

Usage:
    from data.synthetic import DataFactory

    factory = DataFactory()
    profile  = factory.company_profile("2222.SE")         # Saudi Aramco
    news     = factory.news_items("2222.SE", n=5)
    holdings = factory.portfolio()
"""
from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from typing import Any

from data.synthetic.models import (
    AlertEvent,
    AnalystEstimates,
    BalanceSheet,
    CashFlow,
    CRMDealRecord,
    ComparableCompany,
    CompanyProfile,
    ConflictOfInterestEntry,
    Covenant,
    DocumentRecord,
    EarningsTranscript,
    ExtractedFinancials,
    IncomeStatement,
    MAndATransaction,
    NewsItem,
    PortfolioHolding,
    PriceData,
    QAEntry,
    RiskFactor,
    SanctionsEntry,
    ScreeningUniverseEntry,
    ShariaScreening,
    TadawulSecurity,
    ValuationMultiples,
)

# ---------------------------------------------------------------------------
# Master company registry — all figures in USD unless noted
# ---------------------------------------------------------------------------

_COMPANIES: dict[str, dict[str, Any]] = {
    "2222.SE": {
        "name": "Saudi Aramco",
        "name_ar": "أرامكو السعودية",
        "symbol": "2222",
        "isin": "SA0007879101",
        "sedol": "BYVJC57",
        "sector": "Energy",
        "tasi_sector": "Energy",
        "sub_sector": "Oil, Gas & Consumable Fuels",
        "industry": "Integrated Oil & Gas",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 1_850_000_000_000,
        "shares_outstanding": 8_500_000_000_000,
        "free_float_pct": 1.5,
        "par_value_sar": 2.0,
        "listing_date": date(2019, 12, 11),
        "index_member": ["TASI", "MSCI EM", "FTSE EM"],
        "sharia_compliant": True,
        "price_sar": 31.50,
        "52w_high_sar": 34.10,
        "52w_low_sar": 27.80,
        "revenue": 420.5e9,
        "ebitda": 195.0e9,
        "net_income": 121.3e9,
        "total_debt": 92.0e9,
        "cash": 48.2e9,
        "capex": 40.2e9,
        "ev_ebitda": 12.4,
        "pe_ratio": 16.2,
        "company_id": "IQ10001",
        "debt_to_assets_ratio": 0.18,
        "non_permissible_revenue_pct": 0.0,
        "irr": 22.1,
        "moic": 1.85,
    },
    "1120.SE": {
        "name": "Al Rajhi Bank",
        "name_ar": "مصرف الراجحي",
        "symbol": "1120",
        "isin": "SA0007879201",
        "sedol": "6437414",
        "sector": "Banks",
        "tasi_sector": "Banks",
        "sub_sector": "Islamic Banking",
        "industry": "Islamic Commercial Banking",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 85_000_000_000,
        "shares_outstanding": 1_500_000_000,
        "free_float_pct": 25.0,
        "par_value_sar": 10.0,
        "listing_date": date(2006, 4, 23),
        "index_member": ["TASI", "MSCI EM"],
        "sharia_compliant": True,
        "price_sar": 95.20,
        "52w_high_sar": 108.40,
        "52w_low_sar": 82.60,
        "revenue": 12.3e9,
        "ebitda": 9.8e9,
        "net_income": 6.1e9,
        "total_debt": 0.0,
        "cash": 18.5e9,
        "capex": 0.8e9,
        "ev_ebitda": 13.8,
        "pe_ratio": 20.3,
        "company_id": "IQ10002",
        "debt_to_assets_ratio": 0.0,
        "non_permissible_revenue_pct": 0.0,
        "irr": 19.8,
        "moic": 2.10,
    },
    "7010.SE": {
        "name": "STC (Saudi Telecom Company)",
        "name_ar": "شركة الاتصالات السعودية",
        "symbol": "7010",
        "isin": "SA0007879301",
        "sedol": "6437415",
        "sector": "Telecommunication Services",
        "tasi_sector": "Telecommunication Services",
        "sub_sector": "Integrated Telecom",
        "industry": "Integrated Telecommunications",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 58_000_000_000,
        "shares_outstanding": 4_000_000_000,
        "free_float_pct": 37.0,
        "par_value_sar": 10.0,
        "listing_date": date(2003, 8, 4),
        "index_member": ["TASI", "MSCI EM"],
        "sharia_compliant": True,
        "price_sar": 44.15,
        "52w_high_sar": 52.80,
        "52w_low_sar": 38.90,
        "revenue": 15.8e9,
        "ebitda": 6.2e9,
        "net_income": 3.4e9,
        "total_debt": 14.5e9,
        "cash": 5.8e9,
        "capex": 3.2e9,
        "ev_ebitda": 10.9,
        "pe_ratio": 17.6,
        "company_id": "IQ10003",
        "debt_to_assets_ratio": 0.28,
        "non_permissible_revenue_pct": 0.0,
        "irr": 14.2,
        "moic": 1.38,
    },
    "4030.SE": {
        "name": "SABIC",
        "name_ar": "سابك",
        "symbol": "4030",
        "isin": "SA0007879401",
        "sedol": "6437416",
        "sector": "Materials",
        "tasi_sector": "Materials",
        "sub_sector": "Specialty Chemicals",
        "industry": "Diversified Chemicals",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 42_000_000_000,
        "shares_outstanding": 3_000_000_000,
        "free_float_pct": 30.0,
        "par_value_sar": 10.0,
        "listing_date": date(1984, 1, 1),
        "index_member": ["TASI"],
        "sharia_compliant": True,
        "price_sar": 52.80,
        "52w_high_sar": 67.20,
        "52w_low_sar": 44.10,
        "revenue": 33.4e9,
        "ebitda": 6.8e9,
        "net_income": 1.9e9,
        "total_debt": 25.3e9,
        "cash": 8.1e9,
        "capex": 4.8e9,
        "ev_ebitda": 8.6,
        "pe_ratio": 22.1,
        "company_id": "IQ10004",
        "debt_to_assets_ratio": 0.31,
        "non_permissible_revenue_pct": 0.0,
        "irr": 11.4,
        "moic": 1.22,
    },
    "2010.SE": {
        "name": "SABIC Agri-Nutrients",
        "name_ar": "سابك للمغذيات الزراعية",
        "symbol": "2010",
        "isin": "SA0007879501",
        "sedol": "6437417",
        "sector": "Materials",
        "tasi_sector": "Materials",
        "sub_sector": "Fertilizers & Agricultural Chemicals",
        "industry": "Fertilizers",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 16_500_000_000,
        "shares_outstanding": 600_000_000,
        "free_float_pct": 20.0,
        "par_value_sar": 10.0,
        "listing_date": date(2009, 6, 14),
        "index_member": ["TASI"],
        "sharia_compliant": True,
        "price_sar": 104.00,
        "52w_high_sar": 128.40,
        "52w_low_sar": 91.20,
        "revenue": 6.1e9,
        "ebitda": 3.4e9,
        "net_income": 2.5e9,
        "total_debt": 1.2e9,
        "cash": 2.8e9,
        "capex": 0.5e9,
        "ev_ebitda": 9.2,
        "pe_ratio": 13.8,
        "company_id": "IQ10005",
        "debt_to_assets_ratio": 0.12,
        "non_permissible_revenue_pct": 0.0,
        "irr": 17.6,
        "moic": 1.62,
    },
    "4200.SE": {
        "name": "ACWA Power",
        "name_ar": "أكوا باور",
        "symbol": "4200",
        "isin": "SA0007879601",
        "sedol": "6437418",
        "sector": "Utilities",
        "tasi_sector": "Utilities",
        "sub_sector": "Independent Power Producers & Energy Traders",
        "industry": "Renewable Energy",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 22_000_000_000,
        "shares_outstanding": 1_420_000_000,
        "free_float_pct": 15.0,
        "par_value_sar": 10.0,
        "listing_date": date(2021, 11, 15),
        "index_member": ["TASI", "MSCI EM"],
        "sharia_compliant": True,
        "price_sar": 58.30,
        "52w_high_sar": 74.10,
        "52w_low_sar": 48.50,
        "revenue": 2.8e9,
        "ebitda": 1.9e9,
        "net_income": 0.58e9,
        "total_debt": 18.4e9,
        "cash": 3.2e9,
        "capex": 5.1e9,
        "ev_ebitda": 19.4,
        "pe_ratio": 37.9,
        "company_id": "IQ10006",
        "debt_to_assets_ratio": 0.62,
        "non_permissible_revenue_pct": 0.0,
        "irr": 24.3,
        "moic": 2.42,
    },
    "7020.SE": {
        "name": "Elm Company",
        "name_ar": "شركة علم",
        "symbol": "7020",
        "isin": "SA0007879701",
        "sedol": "6437419",
        "sector": "Software & Services",
        "tasi_sector": "Software & Services",
        "sub_sector": "IT Services",
        "industry": "Digital Government Services",
        "country": "Saudi Arabia",
        "exchange": "Tadawul",
        "currency": "SAR",
        "market_cap_usd": 9_800_000_000,
        "shares_outstanding": 100_000_000,
        "free_float_pct": 30.0,
        "par_value_sar": 10.0,
        "listing_date": date(2022, 2, 1),
        "index_member": ["TASI"],
        "sharia_compliant": True,
        "price_sar": 372.00,
        "52w_high_sar": 410.80,
        "52w_low_sar": 295.00,
        "revenue": 1.2e9,
        "ebitda": 0.42e9,
        "net_income": 0.31e9,
        "total_debt": 0.31e9,
        "cash": 0.95e9,
        "capex": 0.12e9,
        "ev_ebitda": 21.8,
        "pe_ratio": 31.6,
        "company_id": "IQ10007",
        "debt_to_assets_ratio": 0.14,
        "non_permissible_revenue_pct": 0.0,
        "irr": 18.4,
        "moic": 1.48,
    },
}

_TICKERS = list(_COMPANIES.keys())

_NEWS_TEMPLATES: list[dict[str, Any]] = [
    {
        "headline": "{name} reports Q2 EBITDA beat of 12% vs. consensus",
        "sentiment": "positive",
        "tags": ["earnings", "ebitda"],
    },
    {
        "headline": "{name} raises full-year dividend guidance amid strong cash generation",
        "sentiment": "positive",
        "tags": ["dividend", "guidance"],
    },
    {
        "headline": "{name} faces regulatory probe into pricing practices",
        "sentiment": "negative",
        "tags": ["regulatory", "risk"],
    },
    {
        "headline": "Analyst upgrades {name} to Buy; price target SAR {pt}",
        "sentiment": "positive",
        "tags": ["analyst", "upgrade"],
    },
    {
        "headline": "{name} management signals cautious capex outlook for H2",
        "sentiment": "neutral",
        "tags": ["capex", "guidance"],
    },
    {
        "headline": "MSCI rebalancing adds weight to {name}; passive inflows expected",
        "sentiment": "positive",
        "tags": ["index", "flows"],
    },
    {
        "headline": "{name} announces SAR 2bn share buyback programme",
        "sentiment": "positive",
        "tags": ["buyback", "capital_allocation"],
    },
    {
        "headline": "Moody's affirms {name} Aa3 rating with stable outlook",
        "sentiment": "neutral",
        "tags": ["credit_rating", "moody's"],
    },
]

_ANALYSTS = [
    ("Ahmed Al-Rashid", "SNB Capital"),
    ("Sarah Johnson", "Goldman Sachs"),
    ("Omar Bafilil", "EFG Hermes"),
    ("Priya Sharma", "Morgan Stanley"),
    ("Khalid Al-Otaibi", "Jadwa Investment"),
    ("Charlotte Davies", "Barclays"),
    ("Faisal Al-Hamdan", "Alistithmar Capital"),
]

_EXECUTIVES = {
    "2222.SE": [{"name": "Amin Nasser", "role": "CEO"}, {"name": "Ziad Al-Murshed", "role": "CFO"}],
    "1120.SE": [{"name": "Waleed Al-Mogbel", "role": "CEO"}, {"name": "Khaled Al-Gosaibi", "role": "CFO"}],
    "7010.SE": [{"name": "Olayan Al-Wetaid", "role": "CEO"}, {"name": "Nasser Al-Qahtani", "role": "CFO"}],
    "4030.SE": [{"name": "Abdulrahman Al-Fageeh", "role": "CEO"}, {"name": "John Cooper", "role": "CFO"}],
    "2010.SE": [{"name": "Bandar Al-Harbi", "role": "CEO"}, {"name": "Mazen Al-Ghamdi", "role": "CFO"}],
    "4200.SE": [{"name": "Marco Arcelli", "role": "CEO"}, {"name": "Rajit Nanda", "role": "CFO"}],
    "7020.SE": [{"name": "Badr Al-Badr", "role": "CEO"}, {"name": "Khalid Al-Hamdan", "role": "CFO"}],
}

_rng = random.Random(42)  # seeded for reproducibility


def _jitter(base: float, pct: float = 0.05) -> float:
    """Return base value ± pct%."""
    return round(base * (1 + _rng.uniform(-pct, pct)), 4)


def _today() -> date:
    return date.today()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _days_ago(n: int) -> datetime:
    return _now() - timedelta(days=n)


# ---------------------------------------------------------------------------
# DataFactory
# ---------------------------------------------------------------------------

class DataFactory:
    """
    Central factory for synthetic market, portfolio, and document data.

    All public methods return Pydantic models ready to be serialised and
    injected into agent prompts or returned from mock API adapters.
    """

    # ------------------------------------------------------------------
    # 1. Bloomberg / Refinitiv
    # ------------------------------------------------------------------

    def company_profile(self, ticker: str) -> CompanyProfile:
        c = _COMPANIES[ticker]
        return CompanyProfile(
            ticker=ticker,
            isin=c["isin"],
            sedol=c["sedol"],
            name=c["name"],
            sector=c["sector"],
            industry=c["industry"],
            country=c["country"],
            exchange=c["exchange"],
            currency=c["currency"],
            market_cap_usd=_jitter(c["market_cap_usd"]),
        )

    def price_data(self, ticker: str, days: int = 30) -> list[PriceData]:
        c = _COMPANIES[ticker]
        base = c["price_sar"]
        records = []
        for i in range(days):
            d = _today() - timedelta(days=days - i)
            close = _jitter(base, 0.03)
            open_ = _jitter(close, 0.01)
            high = max(open_, close) * _rng.uniform(1.001, 1.02)
            low = min(open_, close) * _rng.uniform(0.98, 0.999)
            vol = int(_jitter(45_000_000, 0.5))
            records.append(
                PriceData(
                    ticker=ticker,
                    date=d,
                    open=round(open_, 2),
                    high=round(high, 2),
                    low=round(low, 2),
                    close=round(close, 2),
                    volume=vol,
                    vwap=round((high + low + close) / 3, 2),
                    **{"52w_high": c["52w_high_sar"], "52w_low": c["52w_low_sar"]},
                )
            )
            base = close
        return records

    def income_statement(self, ticker: str, period: str = "LTM") -> IncomeStatement:
        c = _COMPANIES[ticker]
        rev = _jitter(c["revenue"])
        ebitda = _jitter(c["ebitda"])
        ebit = ebitda * _rng.uniform(0.78, 0.88)
        dna = ebitda - ebit
        ni = _jitter(c["net_income"])
        return IncomeStatement(
            ticker=ticker,
            period=period,
            revenue=round(rev, 2),
            gross_profit=round(rev * _rng.uniform(0.42, 0.62), 2),
            ebitda=round(ebitda, 2),
            ebit=round(ebit, 2),
            interest_expense=round(c["total_debt"] * _rng.uniform(0.03, 0.06), 2),
            net_income=round(ni, 2),
            eps=round(ni / c["shares_outstanding"], 4),
            dna=round(dna, 2),
        )

    def balance_sheet(self, ticker: str, period: str = "FY2025") -> BalanceSheet:
        c = _COMPANIES[ticker]
        debt = _jitter(c["total_debt"])
        cash = _jitter(c["cash"])
        equity = _jitter(c["revenue"] * _rng.uniform(0.5, 0.9))
        return BalanceSheet(
            ticker=ticker,
            period=period,
            total_assets=round(debt + equity + cash, 2),
            cash_and_equivalents=round(cash, 2),
            total_debt=round(debt, 2),
            net_debt=round(debt - cash, 2),
            total_equity=round(equity, 2),
            working_capital=round(_jitter(c["revenue"] * 0.05), 2),
        )

    def cash_flow(self, ticker: str, period: str = "FY2025") -> CashFlow:
        c = _COMPANIES[ticker]
        ocf = _jitter(c["ebitda"] * _rng.uniform(0.70, 0.85))
        capex = _jitter(c["capex"])
        divs = _jitter(c["net_income"] * _rng.uniform(0.65, 0.90))
        return CashFlow(
            ticker=ticker,
            period=period,
            operating_cash_flow=round(ocf, 2),
            capex=round(capex, 2),
            free_cash_flow=round(ocf - capex, 2),
            dividends_paid=round(divs, 2),
        )

    def valuation_multiples(self, ticker: str) -> ValuationMultiples:
        c = _COMPANIES[ticker]
        ev_ebitda = _jitter(c["ev_ebitda"])
        return ValuationMultiples(
            ticker=ticker,
            ev_ebitda=round(ev_ebitda, 2),
            ev_ebit=round(ev_ebitda * _rng.uniform(1.15, 1.35), 2),
            ev_revenue=round(ev_ebitda * _rng.uniform(0.40, 0.55), 2),
            pe_ratio=round(_jitter(c["pe_ratio"]), 2),
            pb_ratio=round(_rng.uniform(1.8, 8.0), 2),
            ev_fcf=round(ev_ebitda * _rng.uniform(1.5, 2.5), 2),
            dividend_yield=round(_rng.uniform(1.5, 6.5), 2),
        )

    def analyst_estimates(self, ticker: str, fiscal_year: str = "FY2026") -> AnalystEstimates:
        c = _COMPANIES[ticker]
        n = _rng.randint(8, 28)
        buy = _rng.randint(int(n * 0.5), int(n * 0.8))
        sell = _rng.randint(0, max(1, int(n * 0.15)))
        hold = n - buy - sell
        return AnalystEstimates(
            ticker=ticker,
            fiscal_year=fiscal_year,
            consensus_revenue=round(_jitter(c["revenue"] * 1.05), 2),
            consensus_ebitda=round(_jitter(c["ebitda"] * 1.06), 2),
            consensus_eps=round(_jitter(c["net_income"] / c["shares_outstanding"] * 1.05), 4),
            n_analysts=n,
            buy_ratings=buy,
            hold_ratings=hold,
            sell_ratings=sell,
            price_target_mean=round(_jitter(c["price_sar"] * 1.12), 2),
        )

    def news_items(self, ticker: str, n: int = 5) -> list[NewsItem]:
        c = _COMPANIES[ticker]
        items = []
        for i in range(n):
            tmpl = _rng.choice(_NEWS_TEMPLATES)
            headline = tmpl["headline"].format(
                name=c["name"],
                pt=round(c["price_sar"] * _rng.uniform(1.05, 1.20), 1),
            )
            items.append(
                NewsItem(
                    ticker=ticker,
                    headline=headline,
                    source=_rng.choice(["Bloomberg", "Reuters", "Argaam", "Mubasher"]),
                    published_at=_days_ago(_rng.randint(0, 30)),
                    sentiment=tmpl["sentiment"],
                    relevance_score=round(_rng.uniform(0.65, 0.99), 2),
                    body=f"Full article text for: {headline}. [Synthetic data — replace with live feed.]",
                    tags=tmpl["tags"],
                )
            )
        return items

    # ------------------------------------------------------------------
    # 2. Tadawul
    # ------------------------------------------------------------------

    def tadawul_security(self, ticker: str) -> TadawulSecurity:
        c = _COMPANIES[ticker]
        return TadawulSecurity(
            symbol=c["symbol"],
            symbol_full=ticker,
            name_ar=c["name_ar"],
            name_en=c["name"],
            tasi_sector=c["tasi_sector"],
            sub_sector=c["sub_sector"],
            sharia_compliant=c["sharia_compliant"],
            currency="SAR",
            par_value_sar=c["par_value_sar"],
            shares_outstanding=c["shares_outstanding"],
            free_float_pct=c["free_float_pct"],
            index_member=c["index_member"],
            listing_date=c["listing_date"],
        )

    def sharia_screening(self, ticker: str) -> ShariaScreening:
        c = _COMPANIES[ticker]
        return ShariaScreening(
            ticker=ticker,
            sharia_compliant=c["sharia_compliant"],
            debt_to_assets_ratio=_jitter(c["debt_to_assets_ratio"], 0.02),
            non_permissible_revenue_pct=c["non_permissible_revenue_pct"],
            cash_and_receivables_ratio=round(_rng.uniform(0.28, 0.55), 3),
            screening_standard="AAOIFI",
            last_screened_date=_today() - timedelta(days=_rng.randint(0, 30)),
        )

    # ------------------------------------------------------------------
    # 3. CapIQ
    # ------------------------------------------------------------------

    def screening_universe(self, tickers: list[str] | None = None) -> list[ScreeningUniverseEntry]:
        tickers = tickers or _TICKERS
        entries = []
        for t in tickers:
            c = _COMPANIES[t]
            ebitda = _jitter(c["ebitda"])
            rev = _jitter(c["revenue"])
            entries.append(
                ScreeningUniverseEntry(
                    company_id=c["company_id"],
                    name=c["name"],
                    country=c["country"],
                    sector=c["sector"],
                    market_cap_usd=_jitter(c["market_cap_usd"]),
                    ev_usd=_jitter(c["market_cap_usd"] + c["total_debt"] - c["cash"]),
                    revenue_ltm=round(rev, 2),
                    ebitda_ltm=round(ebitda, 2),
                    ebitda_margin=round(ebitda / rev * 100, 1),
                    revenue_growth_1y=round(_rng.uniform(-5.0, 18.0), 1),
                    net_debt_ebitda=round((c["total_debt"] - c["cash"]) / max(ebitda, 1), 2),
                    deal_type_fit=_rng.choices(
                        [["strategic"], ["minority"], ["strategic", "minority"], ["buyout"]],
                        k=1,
                    )[0],
                )
            )
        return entries

    def precedent_transactions(self, sector: str | None = None, n: int = 6) -> list[MAndATransaction]:
        deals = [
            MAndATransaction(
                deal_id="TXN-20240315",
                announced_date=date(2024, 3, 15),
                closed_date=date(2024, 9, 1),
                target_name="ACWA Power",
                target_sector="Utilities",
                target_country="Saudi Arabia",
                acquirer_name="PIF",
                acquirer_type="financial",
                deal_value_usd=3_200_000_000,
                enterprise_value_usd=8_900_000_000,
                ev_ebitda_multiple=11.2,
                ev_revenue_multiple=4.8,
                stake_acquired_pct=20.0,
                deal_type="minority",
                financing_structure={"equity_pct": 100, "debt_pct": 0},
                premium_to_undisturbed=28.5,
            ),
            MAndATransaction(
                deal_id="TXN-20231102",
                announced_date=date(2023, 11, 2),
                closed_date=date(2024, 2, 28),
                target_name="Elm Company",
                target_sector="Software & Services",
                target_country="Saudi Arabia",
                acquirer_name="Saudi Aramco Digital",
                acquirer_type="strategic",
                deal_value_usd=420_000_000,
                enterprise_value_usd=1_980_000_000,
                ev_ebitda_multiple=21.4,
                ev_revenue_multiple=6.1,
                stake_acquired_pct=8.5,
                deal_type="minority",
                financing_structure={"equity_pct": 100, "debt_pct": 0},
                premium_to_undisturbed=18.3,
            ),
            MAndATransaction(
                deal_id="TXN-20230615",
                announced_date=date(2023, 6, 15),
                closed_date=date(2023, 12, 10),
                target_name="Gulf International Bank",
                target_sector="Banks",
                target_country="Bahrain",
                acquirer_name="Saudi National Bank",
                acquirer_type="strategic",
                deal_value_usd=1_850_000_000,
                enterprise_value_usd=2_400_000_000,
                ev_ebitda_multiple=14.8,
                ev_revenue_multiple=5.2,
                stake_acquired_pct=100.0,
                deal_type="buyout",
                financing_structure={"equity_pct": 60, "debt_pct": 40},
                premium_to_undisturbed=32.1,
            ),
            MAndATransaction(
                deal_id="TXN-20240901",
                announced_date=date(2024, 9, 1),
                closed_date=None,
                target_name="Tamkeen Capital",
                target_sector="Diversified Financials",
                target_country="Saudi Arabia",
                acquirer_name="Riyad Bank",
                acquirer_type="strategic",
                deal_value_usd=680_000_000,
                enterprise_value_usd=950_000_000,
                ev_ebitda_multiple=12.6,
                ev_revenue_multiple=4.1,
                stake_acquired_pct=35.0,
                deal_type="minority",
                financing_structure={"equity_pct": 80, "debt_pct": 20},
                premium_to_undisturbed=22.8,
            ),
            MAndATransaction(
                deal_id="TXN-20221210",
                announced_date=date(2022, 12, 10),
                closed_date=date(2023, 5, 15),
                target_name="Arabian Internet & Communications",
                target_sector="Software & Services",
                target_country="Saudi Arabia",
                acquirer_name="STC",
                acquirer_type="strategic",
                deal_value_usd=1_220_000_000,
                enterprise_value_usd=1_750_000_000,
                ev_ebitda_multiple=18.9,
                ev_revenue_multiple=5.8,
                stake_acquired_pct=55.0,
                deal_type="buyout",
                financing_structure={"equity_pct": 70, "debt_pct": 30},
                premium_to_undisturbed=25.4,
            ),
            MAndATransaction(
                deal_id="TXN-20250115",
                announced_date=date(2025, 1, 15),
                closed_date=None,
                target_name="Leen Health",
                target_sector="Healthcare Equipment & Services",
                target_country="Saudi Arabia",
                acquirer_name="Saudi German Hospital Group",
                acquirer_type="strategic",
                deal_value_usd=290_000_000,
                enterprise_value_usd=510_000_000,
                ev_ebitda_multiple=16.2,
                ev_revenue_multiple=4.9,
                stake_acquired_pct=49.0,
                deal_type="minority",
                financing_structure={"equity_pct": 55, "debt_pct": 45},
                premium_to_undisturbed=19.7,
            ),
        ]
        if sector:
            deals = [d for d in deals if d.target_sector == sector]
        return deals[:n]

    def comparable_companies(self, tickers: list[str] | None = None) -> list[ComparableCompany]:
        tickers = tickers or _TICKERS
        comps = []
        for t in tickers:
            c = _COMPANIES[t]
            ev_ebitda = _jitter(c["ev_ebitda"])
            comps.append(
                ComparableCompany(
                    company_id=c["company_id"],
                    name=c["name"],
                    ev_ebitda_ntm=round(ev_ebitda * _rng.uniform(0.92, 0.98), 2),
                    ev_ebitda_ltm=round(ev_ebitda, 2),
                    ev_revenue_ntm=round(ev_ebitda * _rng.uniform(0.38, 0.52), 2),
                    pe_ntm=round(_jitter(c["pe_ratio"]) * _rng.uniform(0.90, 0.98), 2),
                    revenue_growth_ntm=round(_rng.uniform(2.0, 14.0), 1),
                    ebitda_margin_ltm=round(c["ebitda"] / c["revenue"] * 100, 1),
                    net_debt_ebitda=round((c["total_debt"] - c["cash"]) / max(c["ebitda"], 1), 2),
                    adjusted=_rng.random() > 0.6,
                    adjustments_applied=_rng.choice([
                        [],
                        ["sbc_normalized"],
                        ["sbc_normalized", "one_time_removed"],
                        ["lease_adjusted"],
                    ]),
                )
            )
        return comps

    # ------------------------------------------------------------------
    # 4. Earnings Transcripts
    # ------------------------------------------------------------------

    def earnings_transcript(self, ticker: str, fiscal_period: str = "Q1 2026") -> EarningsTranscript:
        c = _COMPANIES[ticker]
        executives = _EXECUTIVES.get(ticker, [{"name": "CEO Name", "role": "CEO"}])
        analysts = _rng.sample(_ANALYSTS, k=_rng.randint(3, 5))
        qa = []
        for analyst_name, firm in analysts:
            qa.append(
                QAEntry(
                    analyst_name=analyst_name,
                    firm=firm,
                    question=f"Can you provide more color on {fiscal_period} revenue drivers and any changes to your capex guidance?",
                    answer=f"Thank you for the question. We remain confident in our {fiscal_period} trajectory. "
                           f"Revenue was driven by strong volume growth and disciplined pricing. "
                           f"Capex guidance is maintained at current levels with selective flexibility.",
                    sentiment_shift=_rng.choice(["neutral", "confident", "cautious", "defensive"]),
                )
            )
        return EarningsTranscript(
            company=c["name"],
            ticker=ticker,
            event_type="earnings_call",
            event_date=_today() - timedelta(days=_rng.randint(10, 90)),
            fiscal_period=fiscal_period,
            participants=executives + [{"name": a, "role": "Analyst", "firm": f} for a, f in analysts],
            prepared_remarks=(
                f"Good morning. {c['name']} delivered solid {fiscal_period} results. "
                f"Revenue came in at SAR {round(c['revenue'] / 1e9 * _rng.uniform(0.22, 0.28), 1)}bn for the quarter, "
                f"up {round(_rng.uniform(4.0, 18.0), 1)}% year-on-year. EBITDA margin expanded by "
                f"{round(_rng.uniform(50, 250))}bps. We continue to execute on Vision 2030 aligned initiatives."
            ),
            qa_session=qa,
        )

    # ------------------------------------------------------------------
    # 5. Documents
    # ------------------------------------------------------------------

    def document_record(self, issuer: str, doc_type: str = "CIM") -> DocumentRecord:
        return DocumentRecord(
            doc_id=f"DOC-2026-{_rng.randint(100, 999)}",
            doc_type=doc_type,
            issuer=issuer,
            date=_today() - timedelta(days=_rng.randint(0, 180)),
            source="data_room",
            pages=_rng.randint(60, 280),
            language=_rng.choice(["en", "ar", "en_ar"]),
        )

    def extracted_financials(self, doc_id: str, ticker: str) -> ExtractedFinancials:
        c = _COMPANIES.get(ticker, _COMPANIES["7020.SE"])
        return ExtractedFinancials(
            doc_id=doc_id,
            revenue=round(_jitter(c["revenue"]), 2),
            ebitda=round(_jitter(c["ebitda"]), 2),
            net_debt=round(_jitter(c["total_debt"] - c["cash"]), 2),
            currency="SAR",
            period="FY2025",
            source_page=_rng.randint(25, 80),
        )

    def covenants(self, doc_id: str, n: int = 3) -> list[Covenant]:
        templates = [
            ("Net Leverage Ratio", "financial", 4.0, "<=", 2.8),
            ("Interest Coverage Ratio", "financial", 3.0, ">=", 5.4),
            ("Minimum Liquidity", "financial", 200_000_000, ">=", 380_000_000),
            ("Debt Incurrence Basket", "negative", 500_000_000, "<=", 210_000_000),
        ]
        results = []
        for name, ctype, threshold, op, current in _rng.sample(templates, k=min(n, len(templates))):
            headroom = (threshold - current) if op == ">=" else (current - threshold) * -1
            results.append(
                Covenant(
                    doc_id=doc_id,
                    name=name,
                    type=ctype,
                    threshold=threshold,
                    operator=op,
                    current_value=current,
                    headroom=abs(headroom),
                    test_frequency="quarterly",
                    cure_period_days=_rng.choice([20, 30, 45]),
                    source_page=_rng.randint(60, 120),
                )
            )
        return results

    def risk_factors(self, doc_id: str, n: int = 4) -> list[RiskFactor]:
        templates = [
            ("regulatory", "Exposure to changes in Vision 2030 policy priorities and local content requirements.", "medium"),
            ("market", "Oil price volatility and correlation to government spending cycles.", "high"),
            ("operational", "Cybersecurity risks associated with digital transformation initiatives.", "medium"),
            ("geopolitical", "Regional tensions may disrupt logistics and supply chain.", "high"),
            ("esg", "Transition risk from global decarbonisation trajectory.", "medium"),
            ("financial", "Foreign currency risk on USD-denominated debt vs SAR revenue base.", "low"),
        ]
        return [
            RiskFactor(
                doc_id=doc_id,
                category=cat,
                description=desc,
                severity=sev,
                source_page=_rng.randint(10, 50),
            )
            for cat, desc, sev in _rng.sample(templates, k=min(n, len(templates)))
        ]

    # ------------------------------------------------------------------
    # 6. Portfolio
    # ------------------------------------------------------------------

    def portfolio(self) -> list[PortfolioHolding]:
        holdings_data = [
            ("7020.SE", "equity", date(2022, 3, 1), 50_000_000, 74_000_000, 12.5),
            ("4200.SE", "direct_deal", date(2021, 8, 15), 120_000_000, 198_000_000, 8.2),
            ("1120.SE", "equity", date(2020, 11, 1), 85_000_000, 141_000_000, 2.1),
            ("7010.SE", "bond", date(2023, 1, 10), 30_000_000, 31_500_000, 0.0),
            ("2010.SE", "equity", date(2022, 9, 5), 40_000_000, 58_000_000, 1.8),
        ]
        portfolio = []
        for i, (ticker, itype, edate, cost, curr_val, own_pct) in enumerate(holdings_data, start=1):
            c = _COMPANIES[ticker]
            years = (date.today() - edate).days / 365.25
            portfolio.append(
                PortfolioHolding(
                    holding_id=f"HLD-{i:03d}",
                    company_name=c["name"],
                    instrument_type=itype,
                    entry_date=edate,
                    cost_basis_usd=cost,
                    current_value_usd=_jitter(curr_val, 0.05),
                    ownership_pct=own_pct,
                    irr_to_date=round(_jitter(c["irr"], 0.1), 1),
                    moic_to_date=round(curr_val / cost, 2),
                    status=_rng.choice(["green", "green", "amber"]),
                    thesis_status=_rng.choice(["on_track", "on_track", "outperforming"]),
                )
            )
        return portfolio

    def alerts(self, n: int = 5) -> list[AlertEvent]:
        templates = [
            ("earnings_surprise", "Q1 EBITDA beat consensus by {pct}%", "high", "Escalate"),
            ("rating_change", "Moody's upgraded credit rating to Aa2 with positive outlook", "medium", "Monitor"),
            ("covenant_breach", "Net leverage breached 4.0x threshold — cure period initiated", "high", "Urgent review"),
            ("mgmt_change", "CFO resignation announced; interim appointment effective immediately", "high", "Escalate"),
            ("dividend_cut", "Board reduced interim dividend by 25% citing investment cycle", "medium", "Monitor"),
            ("m_and_a", "Company announced unsolicited bid for regional competitor", "medium", "Monitor"),
        ]
        events = []
        for i in range(n):
            ticker = _rng.choice(_TICKERS)
            c = _COMPANIES[ticker]
            etype, desc_tmpl, sev, action = _rng.choice(templates)
            desc = desc_tmpl.format(pct=round(_rng.uniform(8, 25), 1))
            events.append(
                AlertEvent(
                    alert_id=f"ALT-2026-{_rng.randint(1, 999):03d}",
                    company_name=c["name"],
                    event_type=etype,
                    description=desc,
                    severity=sev,
                    triggered_at=_days_ago(_rng.randint(0, 7)),
                    recommended_action=action,
                    source=_rng.choice(["Bloomberg", "Argaam", "Internal monitoring"]),
                )
            )
        return events

    def crm_pipeline(self) -> list[CRMDealRecord]:
        deals_data = [
            ("Tamkeen Capital", "due_diligence", "direct", 75_000_000, date(2026, 9, 30), "Reema Al-Quwaie", "Term sheet discussions underway"),
            ("Leen Health", "term_sheet", "co-invest", 40_000_000, date(2026, 8, 15), "Ahmed Al-Rashid", "Co-invest alongside Sanabil; DD complete"),
            ("GreenTech Arabia", "initial_review", "direct", 25_000_000, date(2027, 1, 31), "Fatima Al-Zahrani", "First management meeting scheduled"),
            ("Noon.com", "sourcing", "secondary", 150_000_000, date(2027, 3, 31), "Khalid Al-Otaibi", "Exploring secondary block from early investor"),
            ("MBC Group", "documentation", "minority", 200_000_000, date(2026, 7, 15), "Reema Al-Quwaie", "SPA under negotiation; IC approved"),
        ]
        return [
            CRMDealRecord(
                deal_id=f"DEAL-2026-{i+1:03d}",
                company_name=name,
                stage=stage,
                deal_type=dtype,
                target_size_usd=size,
                expected_close_date=close_date,
                lead_partner=partner,
                last_updated=_days_ago(_rng.randint(0, 5)),
                notes=notes,
            )
            for i, (name, stage, dtype, size, close_date, partner, notes) in enumerate(deals_data)
        ]

    # ------------------------------------------------------------------
    # 7. Sanctions & Conflicts
    # ------------------------------------------------------------------

    def sanctions_list(self) -> list[SanctionsEntry]:
        return [
            SanctionsEntry(
                entity_name="Fictional Sanctioned Corp",
                alias=["FSC Ltd", "FSC Holdings"],
                list_source="OFAC",
                list_date=date(2023, 4, 12),
                restriction_type="full_block",
                country="Iran",
                reason="Support for weapons proliferation programme",
            ),
            SanctionsEntry(
                entity_name="Gulf Shadow Trading LLC",
                alias=["GSTL"],
                list_source="UN",
                list_date=date(2024, 1, 8),
                restriction_type="sectoral",
                country="Yemen",
                reason="Financing of designated armed group",
            ),
            SanctionsEntry(
                entity_name="Desert Finance SPC",
                alias=[],
                list_source="EU",
                list_date=date(2022, 11, 30),
                restriction_type="asset_freeze",
                country="Syria",
                reason="Evasion of EU sectoral sanctions",
            ),
        ]

    def conflicts_of_interest(self) -> list[ConflictOfInterestEntry]:
        return [
            ConflictOfInterestEntry(
                entity_name="Al Rajhi Bank",
                conflict_type="existing_portfolio",
                description="Firm holds 2.1% stake via Fund III direct equity position",
                info_barrier_required=True,
                applicable_teams=["IB", "AM", "Research"],
            ),
            ConflictOfInterestEntry(
                entity_name="ACWA Power",
                conflict_type="advisory_mandate",
                description="Firm acted as financial advisor on 2023 sukuk issuance",
                info_barrier_required=True,
                applicable_teams=["DCM", "AM"],
            ),
            ConflictOfInterestEntry(
                entity_name="Tamkeen Capital",
                conflict_type="board_seat",
                description="Senior partner holds independent board seat; recusal required for deal decisions",
                info_barrier_required=False,
                applicable_teams=["IB"],
            ),
        ]

    # ------------------------------------------------------------------
    # Convenience: full context bundle for a given ticker
    # ------------------------------------------------------------------

    def full_company_context(self, ticker: str) -> dict:
        """
        Returns a dict with all data source outputs for a single company.
        Pass this into agent state["context"] for comprehensive coverage.
        """
        if ticker not in _COMPANIES:
            raise ValueError(f"Unknown ticker: {ticker}. Available: {list(_COMPANIES.keys())}")

        doc = self.document_record(_COMPANIES[ticker]["name"])
        return {
            "bloomberg": {
                "profile": self.company_profile(ticker).model_dump(),
                "price_data": [p.model_dump() for p in self.price_data(ticker, days=30)],
                "income_statement": self.income_statement(ticker).model_dump(),
                "balance_sheet": self.balance_sheet(ticker).model_dump(),
                "cash_flow": self.cash_flow(ticker).model_dump(),
                "valuation_multiples": self.valuation_multiples(ticker).model_dump(),
                "analyst_estimates": self.analyst_estimates(ticker).model_dump(),
                "news": [n.model_dump() for n in self.news_items(ticker, n=5)],
            },
            "tadawul": {
                "security": self.tadawul_security(ticker).model_dump(),
                "sharia_screening": self.sharia_screening(ticker).model_dump(),
            },
            "capiq": {
                "universe_entry": next(
                    e.model_dump()
                    for e in self.screening_universe([ticker])
                ),
                "comparable_companies": [c.model_dump() for c in self.comparable_companies(_TICKERS)],
                "precedent_transactions": [t.model_dump() for t in self.precedent_transactions()],
            },
            "transcripts": [
                self.earnings_transcript(ticker, "Q1 2026").model_dump(),
                self.earnings_transcript(ticker, "Q4 2025").model_dump(),
            ],
            "documents": {
                "record": doc.model_dump(),
                "financials": self.extracted_financials(doc.doc_id, ticker).model_dump(),
                "covenants": [c.model_dump() for c in self.covenants(doc.doc_id)],
                "risk_factors": [r.model_dump() for r in self.risk_factors(doc.doc_id)],
            },
            "portfolio": {
                "holdings": [h.model_dump() for h in self.portfolio()],
                "alerts": [a.model_dump() for a in self.alerts(n=3)],
                "crm": [d.model_dump() for d in self.crm_pipeline()],
            },
            "sanctions": {
                "sanctions_list": [s.model_dump() for s in self.sanctions_list()],
                "conflicts_of_interest": [c.model_dump() for c in self.conflicts_of_interest()],
            },
        }

    @staticmethod
    def available_tickers() -> list[str]:
        return _TICKERS
