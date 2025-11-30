# -*- coding: utf-8 -*-
"""
================================================================================
GEMINI PROFIT CRYSTALLIZER - Cognitive Arbitrage Engine
================================================================================

WINDOWS 11 + VS CODE COMPATIBLE VERSION

A revolutionary approach to using LLMs for profit discovery. Instead of treating
Gemini as a chatbot (what millions do), we treat it as a PATTERN RECOGNITION
ORACLE that finds non-obvious opportunities hiding in plain sight.

================================================================================
WHAT THIS CODE DOES (DETAILED EXPLANATION)
================================================================================

TRADITIONAL LLM USAGE (What everyone does):
    - Chatbots: "Answer my question"
    - Content generation: "Write me an article"
    - Summarization: "Summarize this document"
    - Code assistance: "Help me code"

THIS SYSTEM'S APPROACH (Innovative cognitive arbitrage):
    - Treats Gemini as a PATTERN RECOGNITION ENGINE
    - Feeds it structured data and asks for NON-OBVIOUS insights
    - Uses specialized prompts designed for ARBITRAGE discovery
    - Chains multiple analysis modules for comprehensive scanning
    - Ranks opportunities by CONTRARIAN SCORE (how unconventional)

================================================================================
THE 5 PROFIT DISCOVERY MODULES
================================================================================

1. INFORMATION ASYMMETRY MINER
   -----------------------------
   CONCEPT: Most profit comes from knowing what others don't know.

   HOW IT WORKS:
   - Takes publicly available data points (anyone can see this)
   - Asks Gemini to find IMPLICIT patterns (what's NOT obvious)
   - Identifies "second-order effects" (consequences of consequences)
   - Finds valuable questions nobody is asking yet

   EXAMPLE:
   Input: ["GPU prices dropped 40%", "AI inference costs falling 10x yearly"]
   Output: "Hidden pattern: The real bottleneck is shifting from compute to
           data quality. Companies hoarding data will win, not those with
           most GPUs. Profit angle: Invest in data cleaning/curation tools."

2. CONTRARIAN SIGNAL DETECTOR
   ----------------------------
   CONCEPT: When everyone zigs, profit by zagging.

   HOW IT WORKS:
   - Takes popular opinions/beliefs in a domain
   - Asks Gemini to find the HIDDEN ASSUMPTIONS behind each belief
   - Identifies CONDITIONS under which beliefs would be WRONG
   - Generates contrarian positions with profit potential

   EXAMPLE:
   Input: Popular belief "AGI is 5-10 years away"
   Output: "Hidden assumption: Current scaling approach will continue.
           Failure condition: Fundamental architectural breakthrough.
           Contrarian play: Invest in neurosymbolic AI research."

3. CROSS-DOMAIN ARBITRAGEUR
   --------------------------
   CONCEPT: Biggest opportunities exist BETWEEN domains, not within them.

   HOW IT WORKS:
   - Takes two seemingly unrelated domains
   - Asks Gemini to find BRIDGES between them
   - Identifies where solved problems in A can solve unsolved problems in B
   - Finds expertise gaps (experts from A rare but valuable in B)

   EXAMPLE:
   Input: Domain A="Gaming", Domain B="Healthcare"
   Output: "Opportunity: Game engagement mechanics applied to medication
           adherence apps. Gaming solved retention; healthcare hasn't.
           Moat: Game designers don't think about healthcare."

4. SEMANTIC VALUE EXTRACTOR
   --------------------------
   CONCEPT: Transform hidden meaning in text into actionable signals.

   HOW IT WORKS:
   - Takes unstructured text (memos, posts, articles)
   - Asks Gemini to extract IMPLICIT signals others miss
   - Identifies sentiment, timing signals, capability reveals
   - Rates signal strength, actionability, and decay rate

   EXAMPLE:
   Input: "Internal memo: Hiring freeze on ML researchers, expanding
          deployment engineering team"
   Output: "Leading indicator: Company shifting from R&D to production.
           Profit mechanism: Their competitors still in R&D phase will
           fall behind. Signal decay: weeks (before public announcement)."

5. OPPORTUNITY PIPELINE
   ----------------------
   CONCEPT: Chain all modules together for comprehensive scanning.

   HOW IT WORKS:
   - Runs all 4 modules sequentially
   - Collects all discovered opportunities
   - Deduplicates similar findings
   - Ranks by: confidence × contrarian_score
   - Higher contrarian = higher potential (less competition)

================================================================================
KEY DATA STRUCTURES
================================================================================

OpportunitySignal (dataclass):
    - domain: str           # Which field/industry this applies to
    - signal_type: str      # Category (HIDDEN_PATTERN, CONTRARIAN, etc.)
    - confidence: float     # 0.0-1.0, how likely this is valid
    - reasoning: str        # Explanation of the opportunity
    - actionable_steps: list # What to do about it
    - estimated_edge: str   # Your competitive advantage
    - contrarian_score: float # 0.0-1.0, how unconventional (higher = better)
    - timestamp: datetime   # When discovered
    - metadata: dict        # Additional context

================================================================================
HOW TO USE IN VS CODE ON WINDOWS 11
================================================================================

SETUP:
    1. Open VS Code
    2. Create a new folder or open this project
    3. Open terminal (Ctrl+`)
    4. Create virtual environment:
       python -m venv venv
       .\\venv\\Scripts\\activate
    5. Install dependencies:
       pip install google-generativeai colorama

RUNNING:
    Option 1 - Demo Mode (No API key needed):
        python gemini_profit_engine.py --demo

    Option 2 - With API Key:
        python gemini_profit_engine.py --api-key YOUR_KEY_HERE

    Option 3 - Interactive Mode:
        python gemini_profit_engine.py --interactive

    Option 4 - Set environment variable:
        set GEMINI_API_KEY=your_key_here
        python gemini_profit_engine.py

================================================================================
"""

# ============================================================================
# IMPORTS - Windows Compatible
# ============================================================================

from __future__ import annotations  # For Python 3.9 compatibility

import sys
import os
import json
import hashlib
import time
import argparse
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from collections import deque
import re

# Windows console encoding fix
if sys.platform == 'win32':
    # Enable ANSI escape sequences on Windows 10+
    os.system('')
    # Set UTF-8 encoding for console
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass  # Python < 3.7

# Try to import colorama for Windows color support
try:
    from colorama import init, Fore, Style
    init(autoreset=True)  # Initialize colorama for Windows
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback - define empty color codes
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''

# Google Generative AI import with fallback
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """
    Central configuration for the system.

    WHAT THIS DOES:
    - Stores all configurable parameters in one place
    - Makes it easy to adjust behavior without changing code
    - Provides sensible defaults for testing
    """

    # Model settings
    DEFAULT_MODEL = "gemini-1.5-flash"  # Fast and cheap for testing
    PREMIUM_MODEL = "gemini-1.5-pro"    # More capable, slower

    # Temperature controls creativity vs consistency
    # Lower = more consistent, Higher = more creative
    TEMPERATURES = {
        "asymmetry_mining": 0.8,    # Creative - finding hidden patterns
        "contrarian_detection": 0.9, # Very creative - challenging beliefs
        "cross_domain": 0.85,        # Creative - bridging domains
        "semantic_extraction": 0.7,  # Balanced - extracting from text
        "report_generation": 0.6,    # More consistent - executive reports
    }

    # Output limits
    MAX_OUTPUT_TOKENS = 2048
    MAX_TEXT_INPUT_LENGTH = 3000  # Characters to analyze

    # Pipeline settings
    MAX_PATTERN_MEMORY = 1000  # How many patterns to remember
    TOP_OPPORTUNITIES_TO_SHOW = 5


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class OpportunitySignal:
    """
    A crystallized profit opportunity discovered by the system.

    WHAT THIS IS:
    Think of this as a "finding" or "insight" that could be profitable.
    Each module produces these as output.

    FIELDS EXPLAINED:
    - domain: The industry/field (e.g., "AI/ML", "Healthcare")
    - signal_type: Category of opportunity found:
        * HIDDEN_PATTERN: Something non-obvious in the data
        * VALUABLE_QUESTION: A question worth answering for money
        * CONTRARIAN_OPPORTUNITY: Betting against the crowd
        * CONSENSUS_TRAP: Where everyone agrees but is wrong
        * CROSS_DOMAIN_*: Bridging two fields
        * SEMANTIC_*: Extracted from unstructured text
        * META_INSIGHT: High-level strategic finding

    - confidence: 0.0 to 1.0
        * 0.0-0.3: Speculative
        * 0.4-0.6: Moderate confidence
        * 0.7-0.9: High confidence
        * 0.9-1.0: Very high confidence

    - contrarian_score: 0.0 to 1.0
        * Higher = more unconventional
        * Higher contrarian often means less competition
        * But also higher risk

    - reasoning: Why this opportunity exists
    - actionable_steps: What to do about it
    - estimated_edge: Your competitive advantage
    """

    domain: str
    signal_type: str
    confidence: float
    reasoning: str
    actionable_steps: List[str]
    estimated_edge: str
    contrarian_score: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def profit_potential_hash(self) -> str:
        """
        Generate a unique fingerprint for this opportunity.

        WHY:
        - Used for deduplication (avoid counting same opportunity twice)
        - Uses SHA-256 hash of key fields
        - Returns first 12 characters (short but unique enough)
        """
        content = f"{self.domain}:{self.signal_type}:{self.reasoning[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "domain": self.domain,
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "actionable_steps": self.actionable_steps,
            "estimated_edge": self.estimated_edge,
            "contrarian_score": self.contrarian_score,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# ============================================================================
# MOCK ORACLE FOR DEMO MODE (No API Key Required)
# ============================================================================

class MockOracle:
    """
    A mock implementation for testing WITHOUT a Gemini API key.

    WHAT THIS DOES:
    - Simulates Gemini responses with realistic fake data
    - Allows you to test the entire pipeline
    - Useful for understanding how the system works
    - Returns plausible (but generated) opportunities

    WHY THIS EXISTS:
    - Not everyone has a Gemini API key immediately
    - Allows testing the code structure and flow
    - Demonstrates what kind of output to expect
    """

    def __init__(self):
        self.call_count = 0
        print(f"{Fore.YELLOW}[DEMO MODE] Using MockOracle - no real API calls{Style.RESET_ALL}")

    def _summon(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate mock responses based on prompt type.

        HOW IT WORKS:
        - Detects what kind of analysis is being requested
        - Returns pre-crafted realistic responses
        - Adds some randomization for variety
        """
        self.call_count += 1

        # Detect prompt type and return appropriate mock response
        if "information arbitrage specialist" in prompt.lower():
            return self._mock_asymmetry_response()
        elif "contrarian analyst" in prompt.lower():
            return self._mock_contrarian_response()
        elif "cross-domain arbitrage" in prompt.lower():
            return self._mock_arbitrage_response()
        elif "semantic value extractor" in prompt.lower():
            return self._mock_semantic_response()
        elif "executive briefing" in prompt.lower():
            return self._mock_report()
        else:
            return '{"error": "Unknown prompt type"}'

    def _mock_asymmetry_response(self) -> str:
        """Generate mock information asymmetry findings."""
        return json.dumps({
            "hidden_patterns": [
                {
                    "pattern": "Declining ML researcher hiring signals shift from research to deployment",
                    "why_hidden": "Job postings analyzed individually, not as industry trend",
                    "profit_angle": "Invest in MLOps and deployment tooling companies",
                    "confidence": 0.75
                },
                {
                    "pattern": "Open-source model quality approaching proprietary at 10x lower cost",
                    "why_hidden": "Media focuses on frontier models, ignores practical equivalence",
                    "profit_angle": "Build services on open models before competitors realize",
                    "confidence": 0.82
                }
            ],
            "unanswered_questions_worth_money": [
                {
                    "question": "What's the actual ROI of enterprise AI implementations?",
                    "who_would_pay": "CFOs, investors, enterprise software vendors",
                    "estimated_value": "$50K-500K per comprehensive study"
                }
            ],
            "synthesis_opportunities": [
                {
                    "insight": "Combining GPU cost drops + inference optimization = commodity AI services",
                    "requires_combining": ["hardware trends", "software efficiency", "market pricing"],
                    "competitive_moat": "First to build commoditized AI infrastructure wins"
                }
            ]
        })

    def _mock_contrarian_response(self) -> str:
        """Generate mock contrarian analysis."""
        return json.dumps({
            "belief_analysis": [
                {
                    "belief": "Big tech will dominate AI",
                    "hidden_assumption": "Scale advantages are permanent and decisive",
                    "failure_conditions": "Regulatory breakup, open-source catches up, specialized beats general",
                    "contrarian_play": "Invest in vertical AI specialists in regulated industries",
                    "confidence": 0.7
                },
                {
                    "belief": "More data always equals better models",
                    "hidden_assumption": "Data quality is uniform and more is always better",
                    "failure_conditions": "Synthetic data works, quality beats quantity, domain expertise matters more",
                    "contrarian_play": "Build high-quality curated datasets for specific domains",
                    "confidence": 0.8
                }
            ],
            "consensus_traps": [
                "Everyone building general-purpose assistants when specialized tools win",
                "Racing to largest models when efficiency improvements compound faster"
            ],
            "overton_blindspots": [
                "Non-AI solutions often beat AI solutions but aren't considered 'innovative'",
                "Human-in-the-loop systems outperform fully automated ones"
            ],
            "temporal_arbitrage_opportunities": [
                "Regulation will create moats - those compliant early win later"
            ]
        })

    def _mock_arbitrage_response(self) -> str:
        """Generate mock cross-domain arbitrage findings."""
        return json.dumps({
            "arbitrage_opportunities": [
                {
                    "type": "solved_problem_transfer",
                    "description": "Game engagement mechanics for healthcare adherence",
                    "from_domain": "Gaming",
                    "to_domain": "Healthcare",
                    "asymmetry_reason": "Gaming solved engagement; healthcare still struggles with adherence",
                    "bridge_mechanism": "Gamification of medication reminders and health tracking",
                    "moat_explanation": "Game designers don't consider healthcare; health tech ignores gaming psychology",
                    "estimated_difficulty": "medium",
                    "estimated_return": "high"
                },
                {
                    "type": "expertise_gap",
                    "description": "Semiconductor yield optimization for biotech manufacturing",
                    "from_domain": "Semiconductor manufacturing",
                    "to_domain": "Biotech production",
                    "asymmetry_reason": "Chip fabs have 99.9% yield; biotech often under 80%",
                    "bridge_mechanism": "Apply statistical process control from chips to bio",
                    "moat_explanation": "Different industries, different conferences, different expertise pools",
                    "estimated_difficulty": "high",
                    "estimated_return": "extreme"
                }
            ]
        })

    def _mock_semantic_response(self) -> str:
        """Generate mock semantic extraction findings."""
        return json.dumps({
            "extracted_signals": [
                {
                    "signal_type": "leading_indicator",
                    "description": "Hiring freeze + deployment focus = imminent product launch",
                    "evidence": "Shifting resources from R&D to production engineering",
                    "strength": 0.85,
                    "actionability": "short_term",
                    "decay_rate": "weeks",
                    "profit_mechanism": "Position before public announcement moves market"
                },
                {
                    "signal_type": "sentiment",
                    "description": "Frustration with enterprise AI reveals service opportunity",
                    "evidence": "'90% of enterprise AI projects fail' + 'consultants making a killing'",
                    "strength": 0.75,
                    "actionability": "immediate",
                    "decay_rate": "months",
                    "profit_mechanism": "AI implementation consulting has undersupplied demand"
                }
            ],
            "meta_insight": "The real money isn't in building AI - it's in making AI work for enterprises"
        })

    def _mock_report(self) -> str:
        """Generate mock executive briefing."""
        return """
## EXECUTIVE SUMMARY
The AI market is transitioning from a research/hype phase to an implementation/value phase.
The biggest opportunities lie not in building new models, but in making existing models work
reliably in enterprise contexts.

## TOP 3 IMMEDIATE ACTIONS
1. **Position in MLOps/Deployment Tools**: Companies shifting from researchers to deployment
   engineers signals infrastructure demand
2. **Build Domain-Specific Solutions**: Vertical AI in regulated industries (healthcare,
   legal, finance) has less competition and higher margins
3. **Offer AI Implementation Services**: 90% project failure rate = massive consulting opportunity

## HIGHEST CONVICTION OPPORTUNITY
**Enterprise AI Implementation Consulting** (Confidence: 85%, Contrarian: 75%)
- The market is flooded with AI tools but starved for expertise in making them work
- Most consultants focus on strategy; the gap is in execution
- Low competition because it's "boring" compared to building new AI

## CONTRARIAN BETS WORTH CONSIDERING
- Open-source models will commoditize proprietary model advantages within 18 months
- Regulation will become a competitive moat, not a burden
- Human-in-the-loop systems will outperform fully automated ones

## RISKS AND BLINDSPOTS
- We may be too early on open-source commoditization
- Regulatory timeline is uncertain and varies by region
- Enterprise budgets could contract if economic conditions worsen
"""


# ============================================================================
# REAL GEMINI ORACLE
# ============================================================================

class GeminiOracle:
    """
    The Oracle - Our interface to Gemini's pattern recognition capabilities.

    WHAT THIS DOES:
    - Connects to Google's Gemini API
    - Sends carefully crafted prompts
    - Receives and parses responses
    - Manages API configuration

    WHY "ORACLE":
    We don't treat Gemini as a chatbot (ask question, get answer).
    We treat it as an Oracle - a pattern-recognition engine that can
    see connections humans miss.

    KEY CONCEPT - TEMPERATURE:
    - Temperature controls randomness/creativity
    - Low (0.0-0.3): Consistent, factual, repetitive
    - Medium (0.4-0.6): Balanced
    - High (0.7-1.0): Creative, varied, sometimes wild

    For arbitrage discovery, we use higher temperatures because
    we WANT unusual, non-obvious connections.
    """

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize the Oracle.

        Args:
            api_key: Your Gemini API key from Google AI Studio
            model: Which Gemini model to use (default: gemini-1.5-flash)
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package not installed.\n"
                "Install with: pip install google-generativeai"
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model or Config.DEFAULT_MODEL)
        self.insight_cache: Dict[str, str] = {}  # Cache responses
        self.pattern_memory = deque(maxlen=Config.MAX_PATTERN_MEMORY)

        print(f"{Fore.GREEN}[LIVE MODE] Connected to Gemini API{Style.RESET_ALL}")

    def _summon(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Invoke the Oracle with a prompt.

        WHAT THIS DOES:
        1. Sends prompt to Gemini API
        2. Uses specified temperature for creativity control
        3. Returns the response text

        Args:
            prompt: The analysis request to send
            temperature: Creativity level (0.0-1.0)

        Returns:
            The Oracle's response as a string
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=0.95,  # Nucleus sampling threshold
                    max_output_tokens=Config.MAX_OUTPUT_TOKENS,
                )
            )
            return response.text
        except Exception as e:
            print(f"{Fore.RED}Oracle error: {e}{Style.RESET_ALL}")
            return '{"error": "' + str(e) + '"}'


# ============================================================================
# MODULE 1: INFORMATION ASYMMETRY MINER
# ============================================================================

class InformationAsymmetryMiner:
    """
    MODULE 1: Find profit in what others don't see.

    =========================================================================
    CONCEPT
    =========================================================================
    Most profit comes from INFORMATION ASYMMETRY - knowing something others
    don't, or seeing something others miss.

    Traditional approach: Find secret information
    Our approach: Find NON-OBVIOUS SYNTHESIS of public information

    The data is public. Everyone CAN see it. But most people don't SYNTHESIZE
    it properly. This module asks Gemini to find hidden patterns.

    =========================================================================
    HOW IT WORKS
    =========================================================================

    INPUT: List of public data points (facts anyone can find)

    PROCESSING: Gemini analyzes for:
        1. IMPLICIT patterns - what's true but not stated?
        2. EXPERT patterns - what would a specialist notice?
        3. SECOND-ORDER effects - what are the consequences of consequences?
        4. UNASKED questions - what questions does this answer that nobody asks?

    OUTPUT: OpportunitySignal objects with:
        - HIDDEN_PATTERN type signals
        - VALUABLE_QUESTION type signals

    =========================================================================
    EXAMPLE
    =========================================================================

    INPUT DATA:
        - "GPU costs dropped 40%"
        - "AI inference costs falling 10x yearly"
        - "Open-source models closing gap with proprietary"

    HIDDEN PATTERN FOUND:
        Pattern: "Commoditization is happening faster than perceived"
        Why Hidden: "Media focuses on frontier capabilities, not cost curves"
        Profit Angle: "Build on commodity models before competitors realize"
        Confidence: 0.8
    """

    def __init__(self, oracle):
        """
        Args:
            oracle: Either GeminiOracle or MockOracle instance
        """
        self.oracle = oracle

    def mine_knowledge_gaps(
        self,
        domain: str,
        public_data: List[str]
    ) -> List[OpportunitySignal]:
        """
        Mine for hidden patterns in public data.

        Args:
            domain: The field/industry to analyze (e.g., "AI/ML Startups")
            public_data: List of publicly known facts/data points

        Returns:
            List of discovered OpportunitySignal objects
        """

        if not public_data:
            return []

        # This prompt is carefully engineered to extract non-obvious insights
        # Notice how we ask for specific types of patterns
        synthesis_prompt = f"""
You are an information arbitrage specialist. Analyze this public data from {domain}
and identify NON-OBVIOUS insights that most people would miss.

PUBLIC DATA:
{chr(10).join(f"- {d}" for d in public_data)}

Your task:
1. What IMPLICIT patterns exist that aren't explicitly stated?
2. What would a domain expert notice that a casual observer wouldn't?
3. What SECOND-ORDER EFFECTS might emerge from these facts?
4. What questions does this data answer that nobody is asking yet?

Format your response as JSON:
{{
    "hidden_patterns": [
        {{"pattern": "...", "why_hidden": "...", "profit_angle": "...", "confidence": 0.0-1.0}}
    ],
    "unanswered_questions_worth_money": [
        {{"question": "...", "who_would_pay": "...", "estimated_value": "..."}}
    ],
    "synthesis_opportunities": [
        {{"insight": "...", "requires_combining": [...], "competitive_moat": "..."}}
    ]
}}
"""

        response = self.oracle._summon(
            synthesis_prompt,
            temperature=Config.TEMPERATURES["asymmetry_mining"]
        )

        # Parse JSON from response (handles markdown code blocks)
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return self._convert_to_signals(data, domain)
        except json.JSONDecodeError as e:
            print(f"{Fore.YELLOW}Warning: Could not parse response: {e}{Style.RESET_ALL}")

        return []

    def _convert_to_signals(
        self,
        data: Dict[str, Any],
        domain: str
    ) -> List[OpportunitySignal]:
        """
        Convert raw JSON response to OpportunitySignal objects.

        This standardizes the output format so all modules produce
        consistent signal objects that can be compared and ranked.
        """
        signals = []

        # Convert hidden patterns
        for pattern in data.get("hidden_patterns", []):
            signals.append(OpportunitySignal(
                domain=domain,
                signal_type="HIDDEN_PATTERN",
                confidence=float(pattern.get("confidence", 0.5)),
                reasoning=f"Pattern: {pattern.get('pattern', '')}\n"
                         f"Why hidden: {pattern.get('why_hidden', '')}",
                actionable_steps=[pattern.get("profit_angle", "")],
                estimated_edge="Information advantage - seeing what others miss",
                contrarian_score=0.7,  # Hidden patterns are inherently contrarian
            ))

        # Convert valuable questions
        for question in data.get("unanswered_questions_worth_money", []):
            signals.append(OpportunitySignal(
                domain=domain,
                signal_type="VALUABLE_QUESTION",
                confidence=0.6,
                reasoning=f"Question: {question.get('question', '')}",
                actionable_steps=[
                    f"Target audience: {question.get('who_would_pay', 'Unknown')}",
                    f"Potential value: {question.get('estimated_value', 'Unknown')}"
                ],
                estimated_edge="First to answer = market authority",
                contrarian_score=0.8,  # Asking unasked questions is contrarian
            ))

        return signals


# ============================================================================
# MODULE 2: CONTRARIAN SIGNAL DETECTOR
# ============================================================================

class ContrarianSignalDetector:
    """
    MODULE 2: Find profit where the crowd is wrong.

    =========================================================================
    CONCEPT
    =========================================================================

    "Be fearful when others are greedy, greedy when others are fearful."
    - Warren Buffett

    The crowd is often wrong, or at least incomplete in their thinking.
    This module identifies:

    1. CONSENSUS TRAPS: Things everyone agrees on that are actually fragile
    2. OVERTON BLINDSPOTS: Good ideas dismissed as "too unconventional"
    3. TEMPORAL ARBITRAGE: Things obvious in 2 years that seem crazy today

    =========================================================================
    HOW IT WORKS
    =========================================================================

    INPUT: List of popular opinions/beliefs in a domain

    PROCESSING: Gemini analyzes each belief for:
        - Hidden ASSUMPTIONS underlying the belief
        - CONDITIONS under which it would be wrong
        - EVIDENCE people might be ignoring
        - PROFITABLE position if belief is wrong

    OUTPUT: OpportunitySignal objects with:
        - CONTRARIAN_OPPORTUNITY type
        - CONSENSUS_TRAP type

    =========================================================================
    WHY CONTRARIAN SCORE MATTERS
    =========================================================================

    We rank opportunities partially by "contrarian score" because:
    - More contrarian = less competition
    - Less competition = higher potential returns
    - BUT also higher risk (crowd might be right)

    A contrarian score of 0.95 means almost no one is doing this.
    Could be genius or could be stupid. That's the trade-off.
    """

    def __init__(self, oracle):
        self.oracle = oracle

    def detect_crowd_blindspots(
        self,
        popular_opinions: List[str],
        domain: str
    ) -> List[OpportunitySignal]:
        """
        Find where crowd wisdom fails.

        Args:
            popular_opinions: List of commonly held beliefs
            domain: The field these beliefs relate to

        Returns:
            List of contrarian OpportunitySignal objects
        """

        if not popular_opinions:
            return []

        contrarian_prompt = f"""
You are a contrarian analyst. The crowd believes these things about {domain}:

POPULAR OPINIONS:
{chr(10).join(f"* {op}" for op in popular_opinions)}

For each opinion, analyze:
1. What ASSUMPTION underlies this belief?
2. Under what CONDITIONS would this belief be WRONG?
3. What EVIDENCE would people be ignoring?
4. If this belief IS wrong, what's the PROFITABLE contrarian position?

Also identify:
- "Consensus traps": Things everyone agrees on that are actually fragile
- "Overton blindspots": Profitable ideas dismissed as too unconventional
- "Temporal arbitrage": Things that will obviously be true in 2 years but seem crazy now

Respond in JSON:
{{
    "belief_analysis": [
        {{
            "belief": "...",
            "hidden_assumption": "...",
            "failure_conditions": "...",
            "contrarian_play": "...",
            "confidence": 0.0-1.0
        }}
    ],
    "consensus_traps": [...],
    "overton_blindspots": [...],
    "temporal_arbitrage_opportunities": [...]
}}
"""

        response = self.oracle._summon(
            contrarian_prompt,
            temperature=Config.TEMPERATURES["contrarian_detection"]
        )

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return self._extract_contrarian_signals(data, domain)
        except json.JSONDecodeError:
            pass

        return []

    def _extract_contrarian_signals(
        self,
        data: Dict[str, Any],
        domain: str
    ) -> List[OpportunitySignal]:
        """Convert contrarian analysis to OpportunitySignals."""
        signals = []

        # Analyze each belief
        for analysis in data.get("belief_analysis", []):
            if analysis.get("contrarian_play"):
                signals.append(OpportunitySignal(
                    domain=domain,
                    signal_type="CONTRARIAN_OPPORTUNITY",
                    confidence=float(analysis.get("confidence", 0.5)),
                    reasoning=(
                        f"Popular belief: {analysis.get('belief', '')}\n"
                        f"Hidden assumption: {analysis.get('hidden_assumption', '')}\n"
                        f"Fails when: {analysis.get('failure_conditions', '')}"
                    ),
                    actionable_steps=[analysis.get("contrarian_play", "")],
                    estimated_edge="Crowd mispositioning - betting against consensus",
                    contrarian_score=0.9,  # Very contrarian by definition
                    metadata={
                        "failure_conditions": analysis.get("failure_conditions", "")
                    }
                ))

        # Add consensus traps
        for trap in data.get("consensus_traps", []):
            if isinstance(trap, str) and trap:
                signals.append(OpportunitySignal(
                    domain=domain,
                    signal_type="CONSENSUS_TRAP",
                    confidence=0.6,
                    reasoning=trap,
                    actionable_steps=[
                        "Monitor for signs of consensus breaking",
                        "Position against consensus when trigger conditions appear"
                    ],
                    estimated_edge="Consensus fragility - first to exit wins",
                    contrarian_score=0.95,  # Maximum contrarian
                ))

        return signals


# ============================================================================
# MODULE 3: CROSS-DOMAIN ARBITRAGEUR
# ============================================================================

class CrossDomainArbitrageur:
    """
    MODULE 3: Find profit bridges between unrelated fields.

    =========================================================================
    CONCEPT
    =========================================================================

    The BIGGEST opportunities often exist BETWEEN domains, not within them.

    Why? Because expertise stays siloed:
    - Gaming experts don't think about healthcare
    - Semiconductor engineers don't work in biotech
    - Legal experts don't know about AI

    This creates ARBITRAGE opportunities where a solved problem in Domain A
    has an unsolved analog in Domain B.

    =========================================================================
    TYPES OF CROSS-DOMAIN ARBITRAGE
    =========================================================================

    1. SOLVED PROBLEM TRANSFER
       - Problem solved in A, unsolved in B
       - Example: Recommendation engines (solved in e-commerce) for legal discovery

    2. RESOURCE ASYMMETRY
       - Cheap in A, expensive in B
       - Example: Data labeling cheap in gaming, expensive in medical AI

    3. EXPERTISE GAP
       - Experts from A are rare but valuable in B
       - Example: Game designers rare in healthcare but would revolutionize adherence

    4. MODEL DISRUPTION
       - Business model from A could disrupt B
       - Example: Subscription model from SaaS applied to legal services

    5. TECH TRANSFER
       - Technology from A could transform B
       - Example: Computer vision from autonomous cars to surgery

    =========================================================================
    WHY THIS WORKS
    =========================================================================

    - Different industries have different conferences
    - Experts rarely cross-pollinate
    - What's "obvious" in one field is "innovative" in another
    - First to bridge domains often captures the market
    """

    def __init__(self, oracle):
        self.oracle = oracle

    def find_cross_domain_arbitrage(
        self,
        domain_a: str,
        domain_b: str
    ) -> List[OpportunitySignal]:
        """
        Find arbitrage opportunities between two domains.

        Args:
            domain_a: First domain (source of solutions/expertise)
            domain_b: Second domain (destination for transfer)

        Returns:
            List of cross-domain OpportunitySignal objects
        """

        arbitrage_prompt = f"""
You are a cross-domain arbitrage specialist. Analyze these two seemingly unrelated domains:

DOMAIN A: {domain_a}
DOMAIN B: {domain_b}

Find opportunities where:
1. A solved problem in Domain A has an unsolved analog in Domain B
2. A cheap resource in Domain A is expensive in Domain B
3. Expertise from Domain A would be valuable but rare in Domain B
4. A business model in Domain A could disrupt Domain B
5. Technology from Domain A could transform Domain B

For each opportunity, explain:
- The ASYMMETRY (why it exists)
- The BRIDGE (how to exploit it)
- The MOAT (why others haven't done this)

JSON response:
{{
    "arbitrage_opportunities": [
        {{
            "type": "solved_problem_transfer|resource_asymmetry|expertise_gap|model_disruption|tech_transfer",
            "description": "...",
            "from_domain": "...",
            "to_domain": "...",
            "asymmetry_reason": "...",
            "bridge_mechanism": "...",
            "moat_explanation": "...",
            "estimated_difficulty": "low|medium|high",
            "estimated_return": "low|medium|high|extreme"
        }}
    ]
}}
"""

        response = self.oracle._summon(
            arbitrage_prompt,
            temperature=Config.TEMPERATURES["cross_domain"]
        )

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return self._convert_arbitrage_signals(data)
        except json.JSONDecodeError:
            pass

        return []

    def _convert_arbitrage_signals(self, data: Dict[str, Any]) -> List[OpportunitySignal]:
        """Convert arbitrage findings to OpportunitySignals."""
        signals = []

        # Map return estimates to confidence scores
        return_confidence_map = {
            "low": 0.4,
            "medium": 0.6,
            "high": 0.8,
            "extreme": 0.95
        }

        for opp in data.get("arbitrage_opportunities", []):
            confidence = return_confidence_map.get(
                opp.get("estimated_return", "medium"),
                0.6
            )

            signals.append(OpportunitySignal(
                domain=f"{opp.get('from_domain', '?')} -> {opp.get('to_domain', '?')}",
                signal_type=f"CROSS_DOMAIN_{opp.get('type', 'ARBITRAGE').upper()}",
                confidence=confidence,
                reasoning=(
                    f"Description: {opp.get('description', '')}\n"
                    f"Asymmetry: {opp.get('asymmetry_reason', '')}"
                ),
                actionable_steps=[
                    f"Bridge mechanism: {opp.get('bridge_mechanism', '')}",
                    f"Moat: {opp.get('moat_explanation', '')}",
                    f"Difficulty: {opp.get('estimated_difficulty', 'unknown')}"
                ],
                estimated_edge=f"Cross-domain advantage | Return: {opp.get('estimated_return', 'unknown')}",
                contrarian_score=0.75,  # Cross-domain is moderately contrarian
                metadata={
                    "difficulty": opp.get("estimated_difficulty", "unknown"),
                    "description": opp.get("description", ""),
                    "type": opp.get("type", "unknown")
                }
            ))

        return signals


# ============================================================================
# MODULE 4: SEMANTIC VALUE EXTRACTOR
# ============================================================================

class SemanticValueExtractor:
    """
    MODULE 4: Mine meaning from noise.

    =========================================================================
    CONCEPT
    =========================================================================

    Text contains more information than the literal words.

    When someone writes an internal memo or Reddit comment, they reveal:
    - IMPLICIT SENTIMENT: Emotions/beliefs not directly stated
    - LEADING INDICATORS: Predictions about future events
    - CAPABILITY SIGNALS: Resources/abilities they have
    - NETWORK SIGNALS: Relationships/connections implied
    - TIMING SIGNALS: Urgency or temporal patterns

    Most people read text literally. This module extracts the SUBTEXT.

    =========================================================================
    HOW IT WORKS
    =========================================================================

    INPUT: Unstructured text (memos, posts, articles, comments)

    PROCESSING: Gemini extracts:
        - Signal type (sentiment, leading indicator, etc.)
        - Description of what was found
        - Evidence from the text
        - Signal strength (0-1)
        - Actionability (immediate/short_term/long_term)
        - Decay rate (how quickly signal loses value)
        - Profit mechanism

    OUTPUT: OpportunitySignal objects with SEMANTIC_* types

    =========================================================================
    EXAMPLE
    =========================================================================

    INPUT TEXT:
        "Internal memo: Hiring freeze on ML researchers, expanding
         deployment engineering team. Q4 focus is inference optimization."

    EXTRACTED SIGNALS:
        1. Leading Indicator (strength: 0.85)
           - Description: "Shift from R&D to production signals imminent launch"
           - Decay: "weeks" (before public announcement)
           - Profit: "Position before market moves on announcement"

        2. Capability Signal (strength: 0.7)
           - Description: "Company has working ML that needs optimization"
           - This reveals they're past research phase
    """

    def __init__(self, oracle):
        self.oracle = oracle

    def extract_hidden_value(
        self,
        raw_text: str,
        context: str = ""
    ) -> List[OpportunitySignal]:
        """
        Extract hidden signals from unstructured text.

        Args:
            raw_text: The text to analyze
            context: Optional context about what this text is (e.g., "tech memo")

        Returns:
            List of semantic OpportunitySignal objects
        """

        if not raw_text or not raw_text.strip():
            return []

        extraction_prompt = f"""
You are a semantic value extractor. This text may contain hidden profitable signals:

CONTEXT: {context or "General text analysis"}

TEXT TO ANALYZE:
---
{raw_text[:Config.MAX_TEXT_INPUT_LENGTH]}
---

Extract:
1. IMPLICIT SENTIMENT: What emotions/beliefs are expressed but not stated?
2. LEADING INDICATORS: What does this text predict about future events?
3. CAPABILITY SIGNALS: What capabilities/resources does the author reveal?
4. NETWORK SIGNALS: What relationships or connections are implied?
5. TIMING SIGNALS: What temporal patterns or urgency is embedded?
6. CONTRARIAN INDICATORS: What does everyone assume that might be wrong?

For each signal found, rate:
- Signal strength (0-1)
- Actionability (can you profit from this?)
- Decay rate (how quickly does this signal lose value?)

JSON response:
{{
    "extracted_signals": [
        {{
            "signal_type": "sentiment|leading_indicator|capability|network|timing|contrarian",
            "description": "...",
            "evidence": "...",
            "strength": 0.0-1.0,
            "actionability": "immediate|short_term|long_term|informational",
            "decay_rate": "hours|days|weeks|months|evergreen",
            "profit_mechanism": "..."
        }}
    ],
    "meta_insight": "What's the ONE big thing most readers would miss?"
}}
"""

        response = self.oracle._summon(
            extraction_prompt,
            temperature=Config.TEMPERATURES["semantic_extraction"]
        )

        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                return self._convert_semantic_signals(data, context)
        except json.JSONDecodeError:
            pass

        return []

    def _convert_semantic_signals(
        self,
        data: Dict[str, Any],
        context: str
    ) -> List[OpportunitySignal]:
        """Convert semantic extraction to OpportunitySignals."""
        signals = []

        for signal in data.get("extracted_signals", []):
            strength = float(signal.get("strength", 0.5))

            signals.append(OpportunitySignal(
                domain=context or "semantic_extraction",
                signal_type=f"SEMANTIC_{signal.get('signal_type', 'UNKNOWN').upper()}",
                confidence=strength,
                reasoning=(
                    f"{signal.get('description', '')}\n"
                    f"Evidence: {signal.get('evidence', 'None provided')}"
                ),
                actionable_steps=[
                    signal.get("profit_mechanism", ""),
                    f"Actionability: {signal.get('actionability', 'unknown')}",
                    f"Signal decay: {signal.get('decay_rate', 'unknown')}"
                ],
                estimated_edge="Semantic arbitrage - reading between the lines",
                contrarian_score=0.6,
                metadata={
                    "evidence": signal.get("evidence", ""),
                    "decay_rate": signal.get("decay_rate", "unknown"),
                    "actionability": signal.get("actionability", "unknown")
                }
            ))

        # Add meta-insight as special high-value signal
        meta = data.get("meta_insight", "")
        if meta:
            signals.append(OpportunitySignal(
                domain=context or "semantic_extraction",
                signal_type="META_INSIGHT",
                confidence=0.7,
                reasoning=meta,
                actionable_steps=["High-level strategic insight from text analysis"],
                estimated_edge="Pattern recognition advantage",
                contrarian_score=0.85,
            ))

        return signals


# ============================================================================
# MODULE 5: OPPORTUNITY PIPELINE
# ============================================================================

class OpportunityPipeline:
    """
    MODULE 5: Chain all modules together for comprehensive scanning.

    =========================================================================
    CONCEPT
    =========================================================================

    Each individual module finds different types of opportunities:
    - Asymmetry Miner: Hidden patterns in data
    - Contrarian Detector: Crowd blindspots
    - Cross-Domain: Bridges between fields
    - Semantic Extractor: Signals in text

    The Pipeline CHAINS them together to:
    1. Run all modules on the same input
    2. Collect all discovered opportunities
    3. Deduplicate similar findings
    4. RANK by profit potential

    =========================================================================
    RANKING ALGORITHM
    =========================================================================

    Final Score = confidence * contrarian_score

    WHY THIS FORMULA:
    - High confidence alone isn't enough (everyone sees obvious opportunities)
    - High contrarian alone isn't enough (might just be wrong)
    - Combined: likely correct AND few competitors

    =========================================================================
    DEDUPLICATION
    =========================================================================

    Sometimes multiple modules find the same opportunity phrased differently.
    We use a hash of (domain + signal_type + reasoning) to deduplicate.
    """

    def __init__(self, oracle):
        """
        Initialize all analysis modules.

        Args:
            oracle: GeminiOracle or MockOracle instance
        """
        self.oracle = oracle
        self.asymmetry_miner = InformationAsymmetryMiner(oracle)
        self.contrarian_detector = ContrarianSignalDetector(oracle)
        self.arbitrageur = CrossDomainArbitrageur(oracle)
        self.semantic_extractor = SemanticValueExtractor(oracle)
        self.opportunity_queue: List[OpportunitySignal] = []

    def run_full_scan(
        self,
        domain: str,
        public_data: List[str],
        popular_opinions: List[str],
        related_domains: List[str],
        raw_texts: List[str]
    ) -> List[OpportunitySignal]:
        """
        Run complete opportunity discovery scan through all modules.

        This is the main entry point that orchestrates the entire analysis.

        Args:
            domain: Primary domain to analyze
            public_data: List of facts for asymmetry mining
            popular_opinions: List of beliefs for contrarian analysis
            related_domains: List of domains for cross-domain arbitrage
            raw_texts: List of texts for semantic extraction

        Returns:
            Ranked list of all discovered opportunities
        """

        all_signals = []

        # Stage 1: Information Asymmetry Mining
        print(f"\n{Fore.CYAN}[1/4] Mining information asymmetries...{Style.RESET_ALL}")
        if public_data:
            signals = self.asymmetry_miner.mine_knowledge_gaps(domain, public_data)
            all_signals.extend(signals)
            print(f"      Found {len(signals)} hidden patterns")
        else:
            print(f"      Skipped (no public data provided)")

        # Stage 2: Contrarian Signal Detection
        print(f"{Fore.CYAN}[2/4] Detecting contrarian signals...{Style.RESET_ALL}")
        if popular_opinions:
            signals = self.contrarian_detector.detect_crowd_blindspots(
                popular_opinions, domain
            )
            all_signals.extend(signals)
            print(f"      Found {len(signals)} contrarian opportunities")
        else:
            print(f"      Skipped (no popular opinions provided)")

        # Stage 3: Cross-Domain Arbitrage
        print(f"{Fore.CYAN}[3/4] Finding cross-domain arbitrage...{Style.RESET_ALL}")
        if related_domains:
            for related in related_domains:
                signals = self.arbitrageur.find_cross_domain_arbitrage(domain, related)
                all_signals.extend(signals)
            print(f"      Found {len(signals)} arbitrage opportunities")
        else:
            print(f"      Skipped (no related domains provided)")

        # Stage 4: Semantic Value Extraction
        print(f"{Fore.CYAN}[4/4] Extracting semantic value...{Style.RESET_ALL}")
        if raw_texts:
            for text in raw_texts:
                signals = self.semantic_extractor.extract_hidden_value(text, domain)
                all_signals.extend(signals)
            print(f"      Extracted {len(signals)} semantic signals")
        else:
            print(f"      Skipped (no raw texts provided)")

        # Deduplicate and rank
        self._deduplicate_and_rank(all_signals)

        return self.opportunity_queue

    def _deduplicate_and_rank(self, signals: List[OpportunitySignal]):
        """
        Remove duplicates and rank by profit potential.

        ALGORITHM:
        1. Hash each signal by (domain, type, reasoning)
        2. Keep only first occurrence of each hash
        3. Sort by (confidence * contrarian_score) descending
        """

        seen_hashes = set()
        unique_signals = []

        for signal in signals:
            hash_val = signal.profit_potential_hash()
            if hash_val not in seen_hashes:
                seen_hashes.add(hash_val)
                unique_signals.append(signal)

        # Rank by: confidence * contrarian_score
        # Higher = better (likely right AND few competitors)
        unique_signals.sort(
            key=lambda s: s.confidence * s.contrarian_score,
            reverse=True
        )

        self.opportunity_queue = unique_signals

        print(f"\n{Fore.GREEN}Deduplication: {len(signals)} -> {len(unique_signals)} unique signals{Style.RESET_ALL}")


# ============================================================================
# MAIN ENGINE: GEMINI PROFIT CRYSTALLIZER
# ============================================================================

class GeminiProfitCrystallizer:
    """
    THE MAIN ENGINE - Transforms information into profit opportunities.

    =========================================================================
    WHAT THIS CLASS DOES
    =========================================================================

    This is the main interface you interact with. It:
    1. Initializes the Oracle (Gemini connection or mock)
    2. Sets up the analysis pipeline
    3. Provides the `crystallize()` method for analysis
    4. Generates human-readable profit reports

    =========================================================================
    USAGE
    =========================================================================

    # Initialize
    crystallizer = GeminiProfitCrystallizer(api_key="your-key")

    # Run analysis
    opportunities = crystallizer.crystallize(
        domain="Your Industry",
        public_data=["fact1", "fact2"],
        popular_opinions=["belief1", "belief2"],
        related_domains=["other_field1"],
        raw_texts=["text to analyze..."]
    )

    # Generate report
    report = crystallizer.generate_profit_report(opportunities)
    print(report)

    =========================================================================
    WHY "CRYSTALLIZER"
    =========================================================================

    Like crystallizing salt from seawater:
    - Raw input: Scattered data, opinions, text (seawater)
    - Process: Analysis modules (evaporation)
    - Output: Concentrated opportunities (crystals)

    We take raw, unfocused information and "crystallize" it into
    clear, actionable profit opportunities.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = None,
        demo_mode: bool = False
    ):
        """
        Initialize the Profit Crystallizer.

        Args:
            api_key: Gemini API key (required unless demo_mode=True)
            model: Which Gemini model to use
            demo_mode: If True, use MockOracle (no API calls)
        """
        if demo_mode or not api_key:
            self.oracle = MockOracle()
            self.demo_mode = True
        else:
            self.oracle = GeminiOracle(api_key, model)
            self.demo_mode = False

        self.pipeline = OpportunityPipeline(self.oracle)

    def crystallize(
        self,
        domain: str,
        public_data: Optional[List[str]] = None,
        popular_opinions: Optional[List[str]] = None,
        related_domains: Optional[List[str]] = None,
        raw_texts: Optional[List[str]] = None
    ) -> List[OpportunitySignal]:
        """
        Transform raw information into crystallized profit opportunities.

        This is the main method you call to run the analysis.

        Args:
            domain: The primary domain/industry to analyze
                    Example: "AI/ML Startups", "Crypto", "Healthcare"

            public_data: List of publicly available facts
                    These feed the Information Asymmetry Miner
                    Example: ["GPU costs dropped 40%", "AI adoption at 35%"]

            popular_opinions: List of commonly held beliefs
                    These feed the Contrarian Signal Detector
                    Example: ["Big tech will dominate AI", "AGI in 5 years"]

            related_domains: List of other fields for cross-domain analysis
                    These feed the Cross-Domain Arbitrageur
                    Example: ["Semiconductor", "Legal", "Healthcare"]

            raw_texts: List of unstructured text to analyze
                    These feed the Semantic Value Extractor
                    Example: ["Internal memo says...", "Reddit post says..."]

        Returns:
            List of OpportunitySignal objects, ranked by profit potential
        """

        # Print header
        mode_str = "[DEMO]" if self.demo_mode else "[LIVE]"
        print(f"""
{'='*72}
  GEMINI PROFIT CRYSTALLIZER {mode_str}
{'='*72}
  Domain: {domain}
  Public data points: {len(public_data or [])}
  Popular opinions: {len(popular_opinions or [])}
  Related domains: {len(related_domains or [])}
  Raw texts: {len(raw_texts or [])}
{'='*72}
""")

        # Run the pipeline
        opportunities = self.pipeline.run_full_scan(
            domain=domain,
            public_data=public_data or [],
            popular_opinions=popular_opinions or [],
            related_domains=related_domains or [],
            raw_texts=raw_texts or []
        )

        # Print summary
        print(f"""
{'='*72}
  CRYSTALLIZATION COMPLETE
{'='*72}
  Total Opportunities Found: {len(opportunities)}
  Top Score: {opportunities[0].confidence * opportunities[0].contrarian_score:.2f if opportunities else 0}
{'='*72}
""")

        return opportunities

    def generate_profit_report(
        self,
        opportunities: List[OpportunitySignal]
    ) -> str:
        """
        Generate a human-readable executive briefing.

        Takes the ranked opportunities and asks Gemini to synthesize
        them into an actionable report format.

        Args:
            opportunities: List of OpportunitySignal objects

        Returns:
            Formatted report string
        """

        if not opportunities:
            return "No opportunities crystallized. Provide more input data."

        report_prompt = f"""
Generate an executive briefing from these crystallized opportunities.
Focus on ACTIONABILITY and PRIORITY.

OPPORTUNITIES:
{json.dumps([{
    "type": o.signal_type,
    "domain": o.domain,
    "confidence": o.confidence,
    "contrarian_score": o.contrarian_score,
    "reasoning": o.reasoning,
    "actions": o.actionable_steps,
    "edge": o.estimated_edge
} for o in opportunities[:10]], indent=2)}

Format as:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. TOP 3 IMMEDIATE ACTIONS (numbered, specific)
3. HIGHEST CONVICTION OPPORTUNITY (which one and why)
4. CONTRARIAN BETS WORTH CONSIDERING (unconventional but high-potential)
5. RISKS AND BLINDSPOTS (what could go wrong)
"""

        return self.oracle._summon(
            report_prompt,
            temperature=Config.TEMPERATURES["report_generation"]
        )


# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_opportunity(opp: OpportunitySignal, index: int):
    """
    Display a single opportunity in a formatted box.

    Uses colorama colors if available for better visibility.
    """
    score = opp.confidence * opp.contrarian_score

    # Color coding based on score
    if score > 0.6:
        color = Fore.GREEN
    elif score > 0.4:
        color = Fore.YELLOW
    else:
        color = Fore.WHITE

    print(f"""
{color}+{'='*68}+
| Opportunity #{index} - {opp.signal_type:<45}|
+{'='*68}+{Style.RESET_ALL}
| Domain: {opp.domain[:58]:<58} |
| Confidence: {opp.confidence:.0%} | Contrarian: {opp.contrarian_score:.0%} | Score: {score:.2f}       |
+{'-'*68}+
| Reasoning:
|   {opp.reasoning[:60]}
|   {opp.reasoning[60:120] if len(opp.reasoning) > 60 else ''}
+{'-'*68}+
| Actions:""")

    for action in opp.actionable_steps[:3]:
        if action:
            print(f"|   - {action[:60]}")

    print(f"""+{'-'*68}+
| Edge: {opp.estimated_edge[:58]:<58} |
+{'='*68}+
""")


def display_opportunities(opportunities: List[OpportunitySignal], limit: int = 5):
    """Display multiple opportunities."""
    print(f"\n{Fore.CYAN}{'='*72}")
    print(f"  TOP {min(limit, len(opportunities))} CRYSTALLIZED OPPORTUNITIES")
    print(f"{'='*72}{Style.RESET_ALL}\n")

    for i, opp in enumerate(opportunities[:limit], 1):
        display_opportunity(opp, i)


# ============================================================================
# SAMPLE DATA FOR TESTING
# ============================================================================

SAMPLE_DATA = {
    "domain": "AI/ML Startups",

    "public_data": [
        "OpenAI valued at $80B+ in 2024",
        "GPU costs dropped 40% in past year",
        "Fine-tuning now possible on consumer hardware",
        "Enterprise AI adoption at 35% globally",
        "AI regulation bills proposed in 27 countries",
        "Open-source models closing gap with proprietary",
        "AI inference costs falling 10x yearly",
    ],

    "popular_opinions": [
        "AGI is 5-10 years away",
        "Big tech will dominate AI",
        "AI will replace most jobs",
        "More data always equals better models",
        "Scaling laws will continue indefinitely",
        "AI safety is the biggest concern",
    ],

    "related_domains": [
        "Semiconductor manufacturing",
        "Legal services",
        "Education technology",
        "Healthcare diagnostics",
    ],

    "raw_texts": [
        """
        Internal memo from tech company: We're seeing diminishing returns
        on our largest models. The team is pivoting to efficiency and
        specialization. Hiring freeze on ML researchers, expanding
        deployment engineering team. Q4 focus is inference optimization.
        """,
        """
        Reddit thread: "Why I left my ML job at BigCorp" - Top comment:
        "Nobody talks about this but 90% of enterprise AI projects fail.
        The problem isn't the models, it's the data pipelines and change
        management. Consultants are making a killing just doing basics."
        """
    ]
}


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def run_demo():
    """Run the system in demo mode with sample data."""
    print(f"""
{Fore.CYAN}{'='*72}
  GEMINI PROFIT CRYSTALLIZER - DEMO MODE
{'='*72}{Style.RESET_ALL}

Running with sample AI/ML startup data...
No API key required for this demo.
""")

    crystallizer = GeminiProfitCrystallizer(demo_mode=True)

    opportunities = crystallizer.crystallize(**SAMPLE_DATA)

    display_opportunities(opportunities, limit=Config.TOP_OPPORTUNITIES_TO_SHOW)

    print(f"\n{Fore.CYAN}{'='*72}")
    print("  GENERATING EXECUTIVE REPORT")
    print(f"{'='*72}{Style.RESET_ALL}\n")

    report = crystallizer.generate_profit_report(opportunities)
    print(report)

    return opportunities


def run_interactive():
    """Run interactive mode where user provides input."""
    print(f"""
{Fore.CYAN}{'='*72}
  GEMINI PROFIT CRYSTALLIZER - INTERACTIVE MODE
{'='*72}{Style.RESET_ALL}
""")

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = input("Enter your Gemini API key (or press Enter for demo): ").strip()

    demo_mode = not api_key

    # Get domain
    domain = input("\nEnter domain to analyze (e.g., 'E-commerce'): ").strip()
    if not domain:
        domain = "Technology"

    # Get public data
    print("\nEnter public data points (one per line, empty line to finish):")
    public_data = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        public_data.append(line)

    # Get opinions
    print("\nEnter popular opinions (one per line, empty line to finish):")
    popular_opinions = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        popular_opinions.append(line)

    # Get related domains
    print("\nEnter related domains (one per line, empty line to finish):")
    related_domains = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        related_domains.append(line)

    # Run analysis
    crystallizer = GeminiProfitCrystallizer(
        api_key=api_key if not demo_mode else None,
        demo_mode=demo_mode
    )

    opportunities = crystallizer.crystallize(
        domain=domain,
        public_data=public_data or None,
        popular_opinions=popular_opinions or None,
        related_domains=related_domains or None,
    )

    display_opportunities(opportunities)

    # Generate report
    if input("\nGenerate executive report? (y/n): ").lower() == 'y':
        report = crystallizer.generate_profit_report(opportunities)
        print(f"\n{report}")

    return opportunities


def main():
    """Main entry point with argument parsing."""

    parser = argparse.ArgumentParser(
        description="Gemini Profit Crystallizer - Cognitive Arbitrage Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gemini_profit_engine.py --demo          Run with sample data (no API key)
  python gemini_profit_engine.py --interactive   Interactive mode
  python gemini_profit_engine.py --api-key KEY   Run with your API key

Environment variable:
  Set GEMINI_API_KEY to avoid passing --api-key

For more information, see the module docstring at the top of this file.
"""
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample data (no API key needed)"
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )

    parser.add_argument(
        "--api-key", "-k",
        type=str,
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )

    parser.add_argument(
        "--model", "-m",
        type=str,
        default=Config.DEFAULT_MODEL,
        help=f"Gemini model to use (default: {Config.DEFAULT_MODEL})"
    )

    args = parser.parse_args()

    # Handle different modes
    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    elif args.api_key or os.environ.get("GEMINI_API_KEY"):
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        crystallizer = GeminiProfitCrystallizer(api_key=api_key, model=args.model)
        opportunities = crystallizer.crystallize(**SAMPLE_DATA)
        display_opportunities(opportunities)
        report = crystallizer.generate_profit_report(opportunities)
        print(f"\n{report}")
    else:
        # No arguments - show help
        print(__doc__)
        print(f"""
{Fore.YELLOW}{'='*72}
  QUICK START
{'='*72}{Style.RESET_ALL}

Run in demo mode (no API key needed):
  python gemini_profit_engine.py --demo

Run interactively:
  python gemini_profit_engine.py --interactive

Run with API key:
  python gemini_profit_engine.py --api-key YOUR_KEY_HERE

{Fore.CYAN}For full documentation, read the docstring at the top of this file.{Style.RESET_ALL}
""")


if __name__ == "__main__":
    main()
