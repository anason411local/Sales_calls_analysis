"""
LangGraph-based extraction agent with state management.
Implements a stateful workflow for processing sales call data.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from ..llm.gemini_client import GeminiClient
from ..utils.logger import logger
from ..schemas.extraction_schemas import FlattenedCallData


# ============================================================================
# STATE DEFINITION
# ============================================================================

class ExtractionState(TypedDict):
    """State for the extraction agent workflow"""
    
    # Input data
    row_index: int
    call_id: Optional[str]
    call_date: str
    call_duration: int
    transcription: str
    agent_name: str
    
    # Processing state
    current_step: str
    retry_count: int
    errors: Annotated[List[str], operator.add]
    
    # Extraction results
    raw_extraction: Optional[Dict[str, Any]]
    flattened_data: Optional[Dict[str, Any]]
    validation_errors: Annotated[List[str], operator.add]
    
    # Output state
    extraction_status: str  # "pending", "in_progress", "success", "failed"
    extraction_notes: str


# ============================================================================
# EXTRACTION AGENT
# ============================================================================

class SalesCallExtractionAgent:
    """
    LangGraph-based agent for extracting sales call data.
    Implements a multi-step workflow with error handling and validation.
    """
    
    def __init__(self):
        """Initialize the extraction agent"""
        self.gemini_client = GeminiClient()
        self.workflow = self._build_workflow()
        logger.info("Extraction agent initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create workflow graph
        workflow = StateGraph(ExtractionState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input_node)
        workflow.add_node("extract_data", self._extract_data_node)
        workflow.add_node("validate_extraction", self._validate_extraction_node)
        workflow.add_node("flatten_data", self._flatten_data_node)
        workflow.add_node("handle_error", self._handle_error_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        # Add edges
        workflow.add_conditional_edges(
            "validate_input",
            self._route_after_validation,
            {
                "extract": "extract_data",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "extract_data",
            self._route_after_extraction,
            {
                "validate": "validate_extraction",
                "retry": "extract_data",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "validate_extraction",
            self._route_after_validation_check,
            {
                "flatten": "flatten_data",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("flatten_data", "finalize")
        workflow.add_edge("handle_error", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    # ========================================================================
    # WORKFLOW NODES
    # ========================================================================
    
    def _validate_input_node(self, state: ExtractionState) -> ExtractionState:
        """Validate input data"""
        logger.debug(f"Node: validate_input - Row {state['row_index']}")
        
        state["current_step"] = "validate_input"
        state["extraction_status"] = "in_progress"
        
        # Check required fields
        errors = []
        
        if not state.get("transcription") or state["transcription"].strip() == "":
            errors.append("Empty transcription")
        
        if not state.get("call_date"):
            errors.append("Missing call_date")
        
        if not state.get("call_duration") or state["call_duration"] <= 0:
            errors.append("Invalid call_duration")
        
        if errors:
            state["errors"] = errors
            state["extraction_status"] = "failed"
            logger.warning(f"Input validation failed for row {state['row_index']}: {', '.join(errors)}")
        else:
            logger.debug(f"Input validation passed for row {state['row_index']}")
        
        return state
    
    def _extract_data_node(self, state: ExtractionState) -> ExtractionState:
        """Extract data using Gemini LLM"""
        logger.debug(f"Node: extract_data - Row {state['row_index']}")
        
        state["current_step"] = "extract_data"
        
        try:
            # Call Gemini to extract data
            extracted_data = self.gemini_client.extract_call_data(
                call_date=state["call_date"],
                call_duration=state["call_duration"],
                transcription=state["transcription"],
                agent_name=state.get("agent_name", "Unknown"),
                call_id=state.get("call_id"),
                retry_count=state.get("retry_count", 0)
            )
            
            if extracted_data:
                state["raw_extraction"] = extracted_data
                logger.debug(f"Extraction successful for row {state['row_index']}")
            else:
                state["errors"] = state.get("errors", []) + ["Extraction returned None"]
                state["extraction_status"] = "failed"
                logger.error(f"Extraction failed for row {state['row_index']}")
            
        except Exception as e:
            error_msg = f"Extraction error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["extraction_status"] = "failed"
            logger.error(f"Exception in extract_data_node: {error_msg}")
        
        return state
    
    def _validate_extraction_node(self, state: ExtractionState) -> ExtractionState:
        """Validate extracted data"""
        logger.debug(f"Node: validate_extraction - Row {state['row_index']}")
        
        state["current_step"] = "validate_extraction"
        
        validation_errors = []
        raw_data = state.get("raw_extraction")
        
        if not raw_data:
            validation_errors.append("No extracted data to validate")
            state["validation_errors"] = validation_errors
            state["extraction_status"] = "failed"
            return state
        
        # Check for required top-level keys
        required_keys = [
            "customer_engagement",
            "call_opening",
            "objection_friction",
            "pace_control",
            "emotional_tone",
            "outcome_timing"
        ]
        
        for key in required_keys:
            if key not in raw_data:
                validation_errors.append(f"Missing required category: {key}")
        
        if validation_errors:
            state["validation_errors"] = validation_errors
            logger.warning(f"Validation errors for row {state['row_index']}: {', '.join(validation_errors)}")
        else:
            logger.debug(f"Validation passed for row {state['row_index']}")
        
        return state
    
    def _flatten_data_node(self, state: ExtractionState) -> ExtractionState:
        """Flatten nested extraction data for CSV output"""
        logger.debug(f"Node: flatten_data - Row {state['row_index']}")
        
        state["current_step"] = "flatten_data"
        
        try:
            raw_data = state["raw_extraction"]
            flattened = self._flatten_extraction_data(raw_data, state)
            state["flattened_data"] = flattened
            state["extraction_status"] = "success"
            logger.debug(f"Data flattened successfully for row {state['row_index']}")
            
        except Exception as e:
            error_msg = f"Flattening error: {str(e)}"
            state["errors"] = state.get("errors", []) + [error_msg]
            state["extraction_status"] = "failed"
            logger.error(f"Exception in flatten_data_node: {error_msg}")
        
        return state
    
    def _handle_error_node(self, state: ExtractionState) -> ExtractionState:
        """Handle errors and prepare fallback data"""
        logger.debug(f"Node: handle_error - Row {state['row_index']}")
        
        state["current_step"] = "handle_error"
        state["extraction_status"] = "failed"
        
        # Create fallback flattened data with NaN values
        flattened = self._create_fallback_data(state)
        state["flattened_data"] = flattened
        
        # Compile error notes
        all_errors = state.get("errors", []) + state.get("validation_errors", [])
        state["extraction_notes"] = f"Extraction failed: {'; '.join(all_errors)}"
        
        logger.warning(f"Error handling completed for row {state['row_index']}")
        
        return state
    
    def _finalize_node(self, state: ExtractionState) -> ExtractionState:
        """Finalize the extraction process"""
        logger.debug(f"Node: finalize - Row {state['row_index']}")
        
        state["current_step"] = "finalized"
        
        # Add extraction timestamp
        if state["flattened_data"]:
            state["flattened_data"]["extraction_timestamp"] = datetime.now().isoformat()
            state["flattened_data"]["extraction_status"] = state["extraction_status"]
            
            if not state.get("extraction_notes"):
                if state["extraction_status"] == "success":
                    state["extraction_notes"] = "Extraction completed successfully"
                else:
                    state["extraction_notes"] = "Extraction completed with errors"
            
            state["flattened_data"]["extraction_notes"] = state["extraction_notes"]
        
        logger.debug(f"Finalization completed for row {state['row_index']}")
        
        return state
    
    # ========================================================================
    # ROUTING FUNCTIONS
    # ========================================================================
    
    def _route_after_validation(self, state: ExtractionState) -> str:
        """Route after input validation"""
        if state["extraction_status"] == "failed":
            return "error"
        return "extract"
    
    def _route_after_extraction(self, state: ExtractionState) -> str:
        """Route after data extraction"""
        if state.get("raw_extraction"):
            return "validate"
        
        # Check if we should retry
        retry_count = state.get("retry_count", 0)
        if retry_count < 2:  # Max 2 retries within the workflow
            state["retry_count"] = retry_count + 1
            logger.info(f"Retrying extraction for row {state['row_index']} (attempt {retry_count + 1})")
            return "retry"
        
        return "error"
    
    def _route_after_validation_check(self, state: ExtractionState) -> str:
        """Route after extraction validation"""
        validation_errors = state.get("validation_errors", [])
        
        # Allow minor validation errors, but log them
        if len(validation_errors) > 3:  # Too many errors
            return "error"
        
        return "flatten"
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def _flatten_extraction_data(
        self,
        raw_data: Dict[str, Any],
        state: ExtractionState
    ) -> Dict[str, Any]:
        """Flatten nested extraction data into flat dictionary for CSV"""
        
        flattened = {}
        
        # Add metadata
        flattened["call_id"] = state.get("call_id")
        flattened["call_date_omc"] = state.get("call_date")
        flattened["length_in_sec_omc"] = state.get("call_duration")
        flattened["fullname_omc"] = state.get("agent_name")
        flattened["transcription_omc"] = state.get("transcription", "")[:500]  # Truncate for CSV
        
        # Helper function to safely get nested values
        def safe_get(data, *keys, default=None):
            """Safely get nested dictionary values"""
            for key in keys:
                if isinstance(data, dict):
                    data = data.get(key, {})
                else:
                    return default
            return data if data != {} else default
        
        # Category I: Customer Engagement & Interest
        # I.1 Talk Ratio
        talk_ratio = safe_get(raw_data, "customer_engagement", "talk_ratio", default={})
        flattened["i1_total_agent_turns"] = talk_ratio.get("total_agent_turns")
        flattened["i1_total_customer_turns"] = talk_ratio.get("total_customer_turns")
        flattened["i1_agent_percentage"] = talk_ratio.get("agent_percentage")
        flattened["i1_customer_percentage"] = talk_ratio.get("customer_percentage")
        flattened["i1_classification"] = talk_ratio.get("classification")
        flattened["i1_agent_verbiage_sample"] = talk_ratio.get("agent_verbiage_sample")
        flattened["i1_customer_verbiage_sample"] = talk_ratio.get("customer_verbiage_sample")
        
        # I.2 Discovery Questions
        discovery = safe_get(raw_data, "customer_engagement", "discovery_questions", default={})
        
        # Goal 1 questions
        for i in range(1, 9):
            q_key = f"goal1_q{i}_business_duration" if i == 1 else f"goal1_q{i}"
            q_data = discovery.get(q_key, {}) if isinstance(discovery.get(q_key), dict) else {}
            flattened[f"i2_goal1_q{i}_asked"] = q_data.get("asked")
            flattened[f"i2_goal1_q{i}_timestamp"] = q_data.get("timestamp")
            flattened[f"i2_goal1_q{i}_verbiage"] = q_data.get("agent_verbiage")
        
        flattened["i2_goal1_total"] = discovery.get("goal1_total")
        
        # Goal 2 questions
        for i in range(1, 7):
            q_key = f"goal2_q{i}"
            q_data = discovery.get(q_key, {}) if isinstance(discovery.get(q_key), dict) else {}
            flattened[f"i2_goal2_q{i}_asked"] = q_data.get("asked")
            flattened[f"i2_goal2_q{i}_timestamp"] = q_data.get("timestamp")
            flattened[f"i2_goal2_q{i}_verbiage"] = q_data.get("agent_verbiage")
        
        flattened["i2_goal2_total"] = discovery.get("goal2_total")
        
        # Goal 3 questions
        for i in range(1, 5):
            q_key = f"goal3_q{i}"
            q_data = discovery.get(q_key, {}) if isinstance(discovery.get(q_key), dict) else {}
            flattened[f"i2_goal3_q{i}_asked"] = q_data.get("asked")
            flattened[f"i2_goal3_q{i}_timestamp"] = q_data.get("timestamp")
            flattened[f"i2_goal3_q{i}_verbiage"] = q_data.get("agent_verbiage")
        
        flattened["i2_goal3_total"] = discovery.get("goal3_total")
        
        # Advanced discovery
        flattened["i2_advanced_initial_pain_asked"] = discovery.get("advanced_initial_pain_point_asked")
        flattened["i2_advanced_initial_verbiage"] = discovery.get("advanced_initial_question_verbiage")
        flattened["i2_advanced_probing_done"] = discovery.get("advanced_probing_done")
        flattened["i2_advanced_probing_verbiage"] = discovery.get("advanced_probing_verbiage")
        flattened["i2_total_discovery_questions"] = discovery.get("total_discovery_questions")
        flattened["i2_quality_assessment"] = discovery.get("quality_assessment")
        
        # I.3 Signals
        signals = safe_get(raw_data, "customer_engagement", "signals", default={})
        
        # Buying signals
        buying_signals = {
            "results": signals.get("buying_asks_about_results", {}),
            "price": signals.get("buying_asks_about_price", {}),
            "next_steps": signals.get("buying_asks_about_next_steps", {}),
            "timeline": signals.get("buying_asks_about_timeline", {}),
            "positive_sentiment": signals.get("buying_positive_sentiment", {})
        }
        
        for key, signal_data in buying_signals.items():
            if isinstance(signal_data, dict):
                flattened[f"i3_buying_{key}_detected"] = signal_data.get("detected")
                flattened[f"i3_buying_{key}_timestamp"] = signal_data.get("timestamp")
                flattened[f"i3_buying_{key}_verbiage"] = signal_data.get("customer_verbiage")
        
        flattened["i3_total_buying_signals"] = signals.get("total_buying_signals")
        
        # Resistance signals
        resistance_signals = {
            "price": signals.get("resistance_price_pushback", {}),
            "not_interested": signals.get("resistance_not_interested", {}),
            "bad_experience": signals.get("resistance_bad_experience", {}),
            "timing": signals.get("resistance_timing_concerns", {}),
            "budget": signals.get("resistance_budget_constraints", {})
        }
        
        for key, signal_data in resistance_signals.items():
            if isinstance(signal_data, dict):
                flattened[f"i3_resistance_{key}_detected"] = signal_data.get("detected")
                flattened[f"i3_resistance_{key}_timestamp"] = signal_data.get("timestamp")
                flattened[f"i3_resistance_{key}_verbiage"] = signal_data.get("customer_verbiage")
        
        flattened["i3_total_resistance_signals"] = signals.get("total_resistance_signals")
        flattened["i3_signal_ratio"] = signals.get("signal_ratio")
        flattened["i3_overall_sentiment"] = signals.get("overall_sentiment")
        
        # Category II: Call Opening & Framing
        call_opening = safe_get(raw_data, "call_opening", default={})
        
        # II.1 Time to Reason
        time_to_reason = call_opening.get("time_to_reason", {})
        flattened["ii1_greeting_timestamp"] = time_to_reason.get("initial_greeting_timestamp")
        flattened["ii1_reason_timestamp"] = time_to_reason.get("reason_stated_timestamp")
        flattened["ii1_time_elapsed_seconds"] = time_to_reason.get("time_elapsed_seconds")
        flattened["ii1_reason_verbiage"] = time_to_reason.get("reason_verbiage")
        flattened["ii1_reason_clear"] = time_to_reason.get("reason_clear")
        flattened["ii1_complete_opening"] = time_to_reason.get("complete_opening_statement")
        
        # II.2 Personalization
        personalization = call_opening.get("personalization", {})
        flattened["ii2_business_type_mentioned"] = personalization.get("business_type_mentioned")
        flattened["ii2_business_type_timestamp"] = personalization.get("business_type_timestamp")
        flattened["ii2_business_type_verbiage"] = personalization.get("business_type_verbiage")
        flattened["ii2_location_mentioned"] = personalization.get("location_mentioned")
        flattened["ii2_location_timestamp"] = personalization.get("location_timestamp")
        flattened["ii2_location_verbiage"] = personalization.get("location_verbiage")
        flattened["ii2_within_30_seconds"] = personalization.get("within_30_seconds")
        flattened["ii2_within_45_seconds"] = personalization.get("within_45_seconds")
        flattened["ii2_personalization_quality"] = personalization.get("personalization_quality")
        
        # II.3 Call Structure
        call_structure = call_opening.get("call_structure", {})
        flattened["ii3_structure_mentioned"] = call_structure.get("structure_mentioned")
        flattened["ii3_structure_timestamp"] = call_structure.get("structure_timestamp")
        flattened["ii3_framing_phrases"] = call_structure.get("framing_phrases")
        flattened["ii3_time_expectation_set"] = call_structure.get("time_expectation_set")
        flattened["ii3_time_expectation_verbiage"] = call_structure.get("time_expectation_verbiage")
        flattened["ii3_purpose_stated"] = call_structure.get("purpose_stated")
        flattened["ii3_purpose_verbiage"] = call_structure.get("purpose_verbiage")
        flattened["ii3_process_outlined"] = call_structure.get("process_outlined")
        flattened["ii3_process_verbiage"] = call_structure.get("process_verbiage")
        
        # Category III: Objection Handling & Friction
        objection_friction = safe_get(raw_data, "objection_friction", default={})
        
        # III.1 Objection Handling
        objection_handling = objection_friction.get("objection_handling", {})
        flattened["iii1_total_objections"] = objection_handling.get("total_objections")
        flattened["iii1_total_acknowledged"] = objection_handling.get("total_acknowledged")
        flattened["iii1_total_rebutted"] = objection_handling.get("total_rebutted")
        flattened["iii1_total_unaddressed"] = objection_handling.get("total_unaddressed")
        flattened["iii1_objections_detail"] = str(objection_handling.get("objections", []))[:500]
        
        # III.2 Acknowledgement
        acknowledgement = objection_friction.get("acknowledgement", {})
        flattened["iii2_acknowledgement_rate"] = acknowledgement.get("acknowledgement_rate")
        flattened["iii2_pattern_thank_you_count"] = acknowledgement.get("pattern_thank_you", {}).get("count")
        flattened["iii2_pattern_frustrating_count"] = acknowledgement.get("pattern_frustrating", {}).get("count")
        flattened["iii2_pattern_long_time_count"] = acknowledgement.get("pattern_long_time", {}).get("count")
        flattened["iii2_pattern_right_count"] = acknowledgement.get("pattern_absolutely_right", {}).get("count")
        flattened["iii2_pattern_understand_count"] = acknowledgement.get("pattern_understand", {}).get("count")
        flattened["iii2_other_patterns"] = str(acknowledgement.get("other_patterns", []))[:200]
        
        # III.3 Friction
        friction = objection_friction.get("friction", {})
        flattened["iii3_total_price_mentions"] = friction.get("total_price_mentions")
        flattened["iii3_price_mentions_final_2min"] = friction.get("price_mentions_final_2min")
        flattened["iii3_total_timeline_mentions"] = friction.get("total_timeline_mentions")
        flattened["iii3_timeline_mentions_final_2min"] = friction.get("timeline_mentions_final_2min")
        flattened["iii3_total_contract_mentions"] = friction.get("total_contract_mentions")
        flattened["iii3_contract_mentions_final_2min"] = friction.get("contract_mentions_final_2min")
        flattened["iii3_roi_discussed"] = friction.get("roi_discussed")
        flattened["iii3_roi_timestamp"] = friction.get("roi_timestamp")
        flattened["iii3_roi_verbiage"] = friction.get("roi_verbiage")
        flattened["iii3_roi_used_customer_data"] = friction.get("roi_used_customer_data")
        flattened["iii3_correlation_to_dropoff"] = friction.get("correlation_to_dropoff")
        
        # Category IV: Pace, Control, and Interruptions
        pace_control = safe_get(raw_data, "pace_control", default={})
        
        # IV.1 Monologue
        monologue = pace_control.get("monologue", {})
        flattened["iv1_total_agent_turns"] = monologue.get("total_agent_turns")
        flattened["iv1_extended_monologues_count"] = monologue.get("extended_monologues_count")
        flattened["iv1_longest_monologue_duration"] = monologue.get("longest_monologue_duration")
        flattened["iv1_longest_monologue_verbiage"] = monologue.get("longest_monologue_verbiage", "")[:500]
        flattened["iv1_average_monologue_length"] = monologue.get("average_monologue_length")
        flattened["iv1_short_monologues"] = monologue.get("short_monologues")
        flattened["iv1_medium_monologues"] = monologue.get("medium_monologues")
        flattened["iv1_long_monologues"] = monologue.get("long_monologues")
        flattened["iv1_very_long_monologues"] = monologue.get("very_long_monologues")
        flattened["iv1_conversation_balance"] = monologue.get("conversation_balance")
        
        # IV.2 Interruptions
        interruptions = pace_control.get("interruptions", {})
        flattened["iv2_total_interruptions"] = interruptions.get("total_interruptions")
        flattened["iv2_interruption_rate"] = interruptions.get("interruption_rate")
        flattened["iv2_pattern_analysis"] = interruptions.get("pattern_analysis")
        flattened["iv2_interruptions_detail"] = str(interruptions.get("interruptions", []))[:500]
        
        # IV.3 Script Deviation
        script_dev = pace_control.get("script_deviation", {})
        for i in range(1, 9):
            stage_key = f"stage_{i}"
            stage_data = script_dev.get(f"stage_{i}_introduction" if i == 1 else stage_key, {})
            if isinstance(stage_data, dict):
                flattened[f"iv3_stage{i}_present"] = stage_data.get("present")
                flattened[f"iv3_stage{i}_timestamp"] = stage_data.get("timestamp")
        
        flattened["iv3_out_of_order_segments"] = str(script_dev.get("out_of_order_segments", []))[:200]
        flattened["iv3_skipped_segments"] = str(script_dev.get("skipped_segments", []))[:200]
        flattened["iv3_repeated_segments"] = str(script_dev.get("repeated_segments", []))[:200]
        flattened["iv3_premature_closing"] = script_dev.get("premature_closing")
        flattened["iv3_premature_closing_timestamp"] = script_dev.get("premature_closing_timestamp")
        flattened["iv3_returned_to_earlier"] = script_dev.get("returned_to_earlier_stage")
        flattened["iv3_return_details"] = script_dev.get("return_details")
        flattened["iv3_flow_assessment"] = script_dev.get("flow_assessment")
        
        # Category V: Emotional Tone & Rapport
        emotional_tone = safe_get(raw_data, "emotional_tone", default={})
        
        # V.1 Rapport
        rapport = emotional_tone.get("rapport_moments", {})
        flattened["v1_name_used"] = rapport.get("customer_name_used")
        flattened["v1_name_usage_count"] = rapport.get("name_usage_count")
        flattened["v1_name_usage_timestamps"] = str(rapport.get("name_usage_timestamps", []))[:200]
        flattened["v1_name_usage_verbiage"] = rapport.get("name_usage_verbiage")
        flattened["v1_context_reference"] = rapport.get("context_reference_made")
        flattened["v1_context_type"] = rapport.get("context_type")
        flattened["v1_context_verbiage"] = rapport.get("context_verbiage")
        flattened["v1_pleasantry"] = rapport.get("pleasantry_small_talk")
        flattened["v1_pleasantry_verbiage"] = rapport.get("pleasantry_verbiage")
        flattened["v1_tone_assessment"] = rapport.get("tone_assessment")
        flattened["v1_personal_greeting"] = rapport.get("personal_greeting")
        flattened["v1_previous_interaction_ref"] = rapport.get("previous_interaction_reference")
        flattened["v1_common_ground"] = rapport.get("common_ground_established")
        flattened["v1_genuine_interest"] = rapport.get("genuine_interest_expressed")
        
        # V.2 Sentiment
        sentiment = emotional_tone.get("sentiment", {})
        flattened["v2_opening_sentiment"] = sentiment.get("opening_segment", {}).get("sentiment")
        flattened["v2_opening_verbiage"] = sentiment.get("opening_segment", {}).get("customer_verbiage_sample")
        flattened["v2_early_middle_sentiment"] = sentiment.get("early_middle_segment", {}).get("sentiment")
        flattened["v2_early_middle_verbiage"] = sentiment.get("early_middle_segment", {}).get("customer_verbiage_sample")
        flattened["v2_late_middle_sentiment"] = sentiment.get("late_middle_segment", {}).get("sentiment")
        flattened["v2_late_middle_verbiage"] = sentiment.get("late_middle_segment", {}).get("customer_verbiage_sample")
        flattened["v2_closing_sentiment"] = sentiment.get("closing_segment", {}).get("sentiment")
        flattened["v2_closing_verbiage"] = sentiment.get("closing_segment", {}).get("customer_verbiage_sample")
        flattened["v2_sentiment_progression"] = sentiment.get("sentiment_progression")
        flattened["v2_notable_shifts"] = str(sentiment.get("notable_shifts", []))[:500]
        
        # V.3 Empathy
        empathy = emotional_tone.get("empathy", {})
        flattened["v3_total_frustrations"] = empathy.get("total_frustrations")
        flattened["v3_total_empathy_responses"] = empathy.get("total_empathy_responses")
        flattened["v3_empathy_response_rate"] = empathy.get("empathy_response_rate")
        flattened["v3_pattern_frustrating_count"] = empathy.get("pattern_frustrating", {}).get("count")
        flattened["v3_pattern_tough_count"] = empathy.get("pattern_sounds_tough", {}).get("count")
        flattened["v3_pattern_hear_lot_count"] = empathy.get("pattern_hear_from_lot", {}).get("count")
        flattened["v3_pattern_understand_count"] = empathy.get("pattern_understand", {}).get("count")
        flattened["v3_other_patterns"] = str(empathy.get("other_patterns", []))[:200]
        flattened["v3_frustrations_detail"] = str(empathy.get("frustration_moments", []))[:500]
        
        # Category VI: Outcome and Timing Markers
        outcome_timing = safe_get(raw_data, "outcome_timing", default={})
        
        # VI.1 Hangup Timing
        hangup = outcome_timing.get("hangup_timing", {})
        flattened["vi1_total_duration"] = hangup.get("total_call_duration")
        flattened["vi1_hangup_timestamp"] = hangup.get("hangup_timestamp")
        flattened["vi1_hangup_initiated_by"] = hangup.get("hangup_initiated_by")
        flattened["vi1_last_completed_stage"] = hangup.get("last_completed_stage")
        flattened["vi1_last_stage_time_range"] = hangup.get("last_stage_timestamp_range")
        flattened["vi1_verbiage_at_hangup"] = hangup.get("verbiage_at_hangup")
        flattened["vi1_stage_at_disconnect"] = hangup.get("stage_at_disconnect")
        flattened["vi1_time_in_final_stage"] = hangup.get("time_in_final_stage")
        
        # VI.2 Commitment
        commitment = outcome_timing.get("commitment", {})
        flattened["vi2_commitment_type"] = commitment.get("commitment_type")
        flattened["vi2_commitment_timestamp"] = commitment.get("commitment_timestamp")
        flattened["vi2_agent_verbiage"] = commitment.get("agent_verbiage")
        flattened["vi2_customer_verbiage"] = commitment.get("customer_verbiage")
        flattened["vi2_commitment_clarity"] = commitment.get("commitment_clarity")
        flattened["vi2_assumptive_gather_details"] = commitment.get("assumptive_gather_details")
        flattened["vi2_assumptive_gather_timestamp"] = commitment.get("assumptive_gather_details_timestamp")
        flattened["vi2_assumptive_get_started"] = commitment.get("assumptive_get_started")
        flattened["vi2_assumptive_started_timestamp"] = commitment.get("assumptive_get_started_timestamp")
        flattened["vi2_assumptive_questions"] = commitment.get("assumptive_any_questions")
        flattened["vi2_assumptive_questions_timestamp"] = commitment.get("assumptive_any_questions_timestamp")
        flattened["vi2_other_assumptive"] = str(commitment.get("other_assumptive_phrases", []))[:200]
        
        # VI.3 Call Result
        call_result = outcome_timing.get("call_result", {})
        flattened["vi3_result_classification"] = call_result.get("result_classification")
        flattened["vi3_disconnect_reason_price"] = call_result.get("disconnect_reason_price")
        flattened["vi3_disconnect_reason_timeline"] = call_result.get("disconnect_reason_timeline")
        flattened["vi3_disconnect_reason_trust"] = call_result.get("disconnect_reason_trust")
        flattened["vi3_disconnect_reason_consult"] = call_result.get("disconnect_reason_consult")
        flattened["vi3_disconnect_reason_not_qualified"] = call_result.get("disconnect_reason_not_qualified")
        flattened["vi3_disconnect_reason_technical"] = call_result.get("disconnect_reason_technical")
        flattened["vi3_disconnect_reason_agent_error"] = call_result.get("disconnect_reason_agent_error")
        flattened["vi3_disconnect_reason_unclear"] = call_result.get("disconnect_reason_unclear")
        flattened["vi3_supporting_verbiage"] = call_result.get("supporting_verbiage")
        
        return flattened
    
    def _create_fallback_data(self, state: ExtractionState) -> Dict[str, Any]:
        """Create fallback data with NaN/None values for failed extractions"""
        
        # Start with basic metadata
        fallback = {
            "call_id": state.get("call_id"),
            "call_date_omc": state.get("call_date"),
            "length_in_sec_omc": state.get("call_duration"),
            "fullname_omc": state.get("agent_name"),
            "transcription_omc": state.get("transcription", "")[:500]
        }
        
        # Add all other fields as None (will be converted to NaN in pandas)
        # This ensures the CSV has all columns even for failed rows
        from ..schemas.extraction_schemas import FlattenedCallData
        for field_name in FlattenedCallData.model_fields.keys():
            if field_name not in fallback:
                fallback[field_name] = None
        
        return fallback
    
    # ========================================================================
    # PUBLIC INTERFACE
    # ========================================================================
    
    def process_call(
        self,
        row_index: int,
        call_id: Optional[str],
        call_date: str,
        call_duration: int,
        transcription: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Process a single sales call through the extraction workflow.
        
        Args:
            row_index: Index of the row being processed
            call_id: Optional call identifier
            call_date: Date of the call
            call_duration: Duration in seconds
            transcription: Call transcription text
            agent_name: Agent's full name
            
        Returns:
            Flattened extracted data dictionary
        """
        
        # Initialize state
        initial_state = ExtractionState(
            row_index=row_index,
            call_id=call_id,
            call_date=call_date,
            call_duration=call_duration,
            transcription=transcription,
            agent_name=agent_name,
            current_step="initialized",
            retry_count=0,
            errors=[],
            raw_extraction=None,
            flattened_data=None,
            validation_errors=[],
            extraction_status="pending",
            extraction_notes=""
        )
        
        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state.get("flattened_data", {})
        except Exception as e:
            logger.error(f"Workflow execution failed for row {row_index}: {str(e)}")
            return self._create_fallback_data(initial_state)

