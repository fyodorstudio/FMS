from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from .setup_models import QuantMethod, RegisteredSetupDTO

class AccordionState(str, Enum):
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"

class MethodSectionContract(BaseModel):
    """
    Standardized contract for each quantitative method section / accordion in the FMS Library.
    Tracks setup counts, performance telemetry, and research documentation linkage.
    """
    method_id: QuantMethod = Field(..., description="The unique enum identifier for the quant method (e.g. M-MSD, M-PYS)")
    name: str = Field(..., description="Full descriptive name of the quant methodology")
    code: str = Field(..., description="Short identifier code (e.g. M-PYS)")
    description: str = Field(..., description="Plain-language explanation of the trading mechanism")
    hypothesis: str = Field(..., description="The underlying market microstructure or macroeconomic hypothesis")
    research_chapter_file: str = Field(..., description="Filename of the associated research paper chapter in docs/RESEARCH PAPER/")
    
    # Quantitative setup production metrics
    setup_count: int = Field(0, description="Total number of active registered setups produced by this method")
    aggregate_net_r: float = Field(0.0, description="Sum of net realized R across all setups belonging to this method")
    average_expectancy_r: float = Field(0.0, description="Mean expected return per trade (E[R]) across all setups")
    average_win_rate: float = Field(0.0, description="Mean win rate across all setups belonging to this method")
    
    # Codified setups produced by this method
    setups: List[RegisteredSetupDTO] = Field(default_factory=list, description="List of registered setups produced by this method")
    
    # UI Presentation state
    ui_accordion_state: AccordionState = Field(AccordionState.EXPANDED, description="Default rendering state for the library UI accordion")

class LibrarySummaryContract(BaseModel):
    """
    Top-level contract summarizing the entire FMS Library across all quantitative methods.
    """
    methods: List[MethodSectionContract] = Field(default_factory=list, description="List of method sections/accordions")
    total_setups: int = Field(0, description="Total active registered setups across all methods")
    total_net_r: float = Field(0.0, description="Total net realized R across the entire portfolio")
    average_portfolio_expectancy: float = Field(0.0, description="Weighted average expectancy per trade")
    last_audit_timestamp: int = Field(..., description="Unix timestamp of the latest decadal audit run")
