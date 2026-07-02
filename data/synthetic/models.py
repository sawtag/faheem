"""
Pydantic models for all synthetic data sources.
Mirrors the schema defined in docs/data_sources.md.
Swap out the factory with real API adapters when ready for production.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Bloomberg / Refinitiv
# ---------------------------------------------------------------------------

class CompanyProfile(BaseModel):
    ticker: str
    isin: str
    sedol: str
    name: str
    sector: str
    industry: str
    country: str
    exchange: str
    currency: str
    market_cap_usd: float


class PriceData(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float
    week_52_high: float = Field(alias="52w_high")
    week_52_low: float = Field(alias="52w_low")

    model_config = {"populate_by_name": True}


class IncomeStatement(BaseModel):
    ticker: str
    period: str
    revenue: float
    gross_profit: float
    ebitda: float
    ebit: float
    interest_expense: float
    net_income: float
    eps: float
    dna: float  # depreciation & amortisation


class BalanceSheet(BaseModel):
    ticker: str
    period: str
    total_assets: float
    cash_and_equivalents: float
    total_debt: float
    net_debt: float
    total_equity: float
    working_capital: float


class CashFlow(BaseModel):
    ticker: str
    period: str
    operating_cash_flow: float
    capex: float
    free_cash_flow: float
    dividends_paid: float


class ValuationMultiples(BaseModel):
    ticker: str
    ev_ebitda: float
    ev_ebit: float
    ev_revenue: float
    pe_ratio: float
    pb_ratio: float
    ev_fcf: float
    dividend_yield: float


class AnalystEstimates(BaseModel):
    ticker: str
    fiscal_year: str
    consensus_revenue: float
    consensus_ebitda: float
    consensus_eps: float
    n_analysts: int
    buy_ratings: int
    hold_ratings: int
    sell_ratings: int
    price_target_mean: float


class NewsItem(BaseModel):
    ticker: str
    headline: str
    source: str
    published_at: datetime
    sentiment: Literal["positive", "negative", "neutral"]
    relevance_score: float = Field(ge=0.0, le=1.0)
    body: str
    tags: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 2. Tadawul (Saudi Exchange)
# ---------------------------------------------------------------------------

class TadawulSecurity(BaseModel):
    symbol: str
    symbol_full: str
    name_ar: str
    name_en: str
    tasi_sector: str
    sub_sector: str
    sharia_compliant: bool
    currency: str = "SAR"
    par_value_sar: float
    shares_outstanding: int
    free_float_pct: float
    index_member: list[str] = Field(default_factory=list)
    listing_date: date


class ShariaScreening(BaseModel):
    ticker: str
    sharia_compliant: bool
    debt_to_assets_ratio: float
    non_permissible_revenue_pct: float
    cash_and_receivables_ratio: float
    screening_standard: str = "AAOIFI"
    last_screened_date: date


# ---------------------------------------------------------------------------
# 3. S&P Capital IQ (CapIQ)
# ---------------------------------------------------------------------------

class ScreeningUniverseEntry(BaseModel):
    company_id: str
    name: str
    country: str
    sector: str
    market_cap_usd: float
    ev_usd: float
    revenue_ltm: float
    ebitda_ltm: float
    ebitda_margin: float
    revenue_growth_1y: float
    net_debt_ebitda: float
    deal_type_fit: list[str] = Field(default_factory=list)


class MAndATransaction(BaseModel):
    deal_id: str
    announced_date: date
    closed_date: date | None
    target_name: str
    target_sector: str
    target_country: str
    acquirer_name: str
    acquirer_type: Literal["strategic", "financial", "sovereign"]
    deal_value_usd: float
    enterprise_value_usd: float
    ev_ebitda_multiple: float
    ev_revenue_multiple: float
    stake_acquired_pct: float
    deal_type: Literal["minority", "buyout", "merger", "carve_out"]
    financing_structure: dict[str, Any] = Field(default_factory=dict)
    premium_to_undisturbed: float


class ComparableCompany(BaseModel):
    company_id: str
    name: str
    ev_ebitda_ntm: float
    ev_ebitda_ltm: float
    ev_revenue_ntm: float
    pe_ntm: float
    revenue_growth_ntm: float
    ebitda_margin_ltm: float
    net_debt_ebitda: float
    adjusted: bool = False
    adjustments_applied: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 4. Earnings Transcripts
# ---------------------------------------------------------------------------

class QAEntry(BaseModel):
    analyst_name: str
    firm: str
    question: str
    answer: str
    sentiment_shift: Literal["neutral", "defensive", "confident", "cautious"]


class EarningsTranscript(BaseModel):
    company: str
    ticker: str
    event_type: Literal["earnings_call", "analyst_day", "central_bank_presser", "investor_day"]
    event_date: date
    fiscal_period: str
    participants: list[dict[str, str]] = Field(default_factory=list)
    prepared_remarks: str
    qa_session: list[QAEntry] = Field(default_factory=list)
    source: str = "Bloomberg Transcripts"


# ---------------------------------------------------------------------------
# 5. Documents (Data Room / Uploaded)
# ---------------------------------------------------------------------------

class DocumentRecord(BaseModel):
    doc_id: str
    doc_type: Literal["CIM", "PPM", "credit_agreement", "filing", "teaser", "loi"]
    issuer: str
    date: date
    source: Literal["data_room", "upload", "public_filing"]
    pages: int
    language: Literal["en", "ar", "en_ar"]


class ExtractedFinancials(BaseModel):
    doc_id: str
    revenue: float
    ebitda: float
    net_debt: float
    currency: str
    period: str
    source_page: int


class Covenant(BaseModel):
    doc_id: str
    name: str
    type: Literal["financial", "negative", "affirmative"]
    threshold: float
    operator: Literal["<=", ">=", "<", ">", "=="]
    current_value: float
    headroom: float
    test_frequency: Literal["quarterly", "semi_annual", "annual"]
    cure_period_days: int
    source_page: int


class RiskFactor(BaseModel):
    doc_id: str
    category: Literal["regulatory", "market", "operational", "esg", "geopolitical", "financial"]
    description: str
    severity: Literal["high", "medium", "low"]
    source_page: int


# ---------------------------------------------------------------------------
# 6. Portfolio / Internal Database
# ---------------------------------------------------------------------------

class PortfolioHolding(BaseModel):
    holding_id: str
    company_name: str
    instrument_type: Literal["equity", "bond", "direct_deal", "fund_commitment"]
    entry_date: date
    cost_basis_usd: float
    current_value_usd: float
    ownership_pct: float
    irr_to_date: float
    moic_to_date: float
    status: Literal["green", "amber", "red"]
    thesis_status: Literal["on_track", "at_risk", "outperforming", "exited"]


class AlertEvent(BaseModel):
    alert_id: str
    company_name: str
    event_type: Literal[
        "earnings_surprise", "rating_change", "mgmt_change",
        "covenant_breach", "regulatory_action", "dividend_cut", "m_and_a"
    ]
    description: str
    severity: Literal["high", "medium", "low"]
    triggered_at: datetime
    recommended_action: Literal["Monitor", "Escalate", "Urgent review", "No action"]
    source: str


class CRMDealRecord(BaseModel):
    deal_id: str
    company_name: str
    stage: Literal["sourcing", "initial_review", "due_diligence", "term_sheet", "documentation", "closed", "passed"]
    deal_type: Literal["direct", "co-invest", "fund", "secondary"]
    target_size_usd: float
    expected_close_date: date | None
    lead_partner: str
    last_updated: datetime
    notes: str


# ---------------------------------------------------------------------------
# 7. Sanctions & Conflicts Lists
# ---------------------------------------------------------------------------

class SanctionsEntry(BaseModel):
    entity_name: str
    alias: list[str] = Field(default_factory=list)
    list_source: Literal["OFAC", "UN", "EU", "SAMA", "HMT"]
    list_date: date
    restriction_type: Literal["full_block", "sectoral", "travel_ban", "asset_freeze"]
    country: str
    reason: str


class ConflictOfInterestEntry(BaseModel):
    entity_name: str
    conflict_type: Literal["existing_portfolio", "advisory_mandate", "board_seat", "family_relation"]
    description: str
    info_barrier_required: bool
    applicable_teams: list[str] = Field(default_factory=list)
