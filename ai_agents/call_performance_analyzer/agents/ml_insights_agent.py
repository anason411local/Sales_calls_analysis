"""
ML Insights Agent - ReAct Pattern
Analyzes ML outputs and generates actionable insights for the final report
"""
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pandas as pd
import json
import numpy as np
from utils.logger import logger
from utils.gemini_client import get_analysis_llm
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class MLInsight(BaseModel):
    """Single ML insight with evidence"""
    category: str = Field(description="Category: correlation, feature_importance, shap, statistical, lime")
    insight: str = Field(description="The insight statement")
    evidence: str = Field(description="Supporting evidence from ML analysis")
    recommendation: str = Field(description="Actionable recommendation")
    importance_score: float = Field(description="Importance score 0-1")
    visualization_path: Optional[str] = Field(default=None, description="Path to supporting visualization")


class MLInsightsCollection(BaseModel):
    """Collection of ML insights organized by report section"""
    top_variables: List[str] = Field(description="Top 10 most important variables")
    key_insights: List[MLInsight] = Field(description="List of key insights")
    statistical_summary: str = Field(description="Statistical summary")
    recommendations_summary: str = Field(description="Overall recommendations")
    visualizations_to_include: List[str] = Field(description="Paths to key visualizations")
    
    # Section-specific insights for organic blending
    agent_performance_insights: Dict = Field(default_factory=dict, description="ML insights for agent performance section")
    call_pattern_insights: Dict = Field(default_factory=dict, description="ML insights for call pattern section")
    lead_quality_insights: Dict = Field(default_factory=dict, description="ML insights for lead quality section")
    lgs_omc_insights: Dict = Field(default_factory=dict, description="ML insights for LGS/OMC section")
    recommendations_insights: Dict = Field(default_factory=dict, description="ML insights for recommendations section")


class MLInsightsAgent:
    """
    ReAct Agent for analyzing ML outputs and generating insights
    
    Reasoning: Analyzes ML data to understand patterns
    Acting: Generates actionable insights and recommendations
    """
    
    def __init__(self, ml_data_path: str = None):
        """
        Initialize ML Insights Agent
        
        Args:
            ml_data_path: Path to ML analysis outputs (default: auto-detect)
        """
        # Auto-detect ML data path if not provided
        if ml_data_path is None:
            # Try multiple possible locations
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "ML V2" / "analysis_outputs" / "level1_variable",
                Path("../ML V2/analysis_outputs/level1_variable"),
                Path("../../ML V2/analysis_outputs/level1_variable"),
                Path("ML V2/analysis_outputs/level1_variable")
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.ml_data_path = path
                    break
            else:
                # Default to first option even if it doesn't exist
                self.ml_data_path = possible_paths[0]
        else:
            self.ml_data_path = Path(ml_data_path)
        
        self.llm = get_analysis_llm()
        logger.info(f"ML Insights Agent initialized with data path: {self.ml_data_path}")
        
        # Check if ML data exists
        if not self.ml_data_path.exists():
            logger.warning(f"ML data path does not exist: {self.ml_data_path}")
            logger.warning("ML insights will be limited")
    
    def analyze_ml_outputs(self) -> MLInsightsCollection:
        """
        Main entry point: Analyze all ML outputs and generate insights
        
        Returns:
            MLInsightsCollection with all insights
        """
        logger.info("=" * 80)
        logger.info("ML INSIGHTS AGENT: STARTING ANALYSIS")
        logger.info("=" * 80)
        
        try:
            # Step 1: REASONING - Load and understand ML data
            ml_data = self._load_ml_data()
            
            if not ml_data:
                logger.warning("No ML data found, returning empty insights")
                return self._create_empty_insights()
            
            # Step 2: REASONING - Analyze each component
            logger.info("Analyzing ML components...")
            
            correlation_insights = self._analyze_correlations(ml_data.get('correlation'), ml_data)
            importance_insights = self._analyze_feature_importance(ml_data.get('importance'))
            shap_insights = self._analyze_shap(ml_data.get('shap'))
            statistical_insights = self._analyze_statistical_tests(ml_data.get('statistical'))
            lime_insights = self._analyze_lime(ml_data.get('lime'))
            
            # Step 3: ACTING - Synthesize insights using LLM
            logger.info("Synthesizing insights with LLM...")
            
            all_insights = (
                correlation_insights + 
                importance_insights + 
                shap_insights + 
                statistical_insights + 
                lime_insights
            )
            
            # Step 4: ACTING - Generate comprehensive insights
            insights_collection = self._synthesize_insights(all_insights, ml_data)
            
            logger.info(f"Generated {len(insights_collection.key_insights)} key insights")
            logger.info("ML INSIGHTS AGENT: ANALYSIS COMPLETE")
            
            return insights_collection
            
        except Exception as e:
            logger.error(f"Error in ML insights analysis: {str(e)}")
            return self._create_empty_insights()
    
    def _load_ml_data(self) -> Dict:
        """
        REASONING: Load ALL ML analysis outputs (comprehensive data loading)
        
        Returns:
            Dictionary with all ML data
        """
        logger.info("Loading ML data files (comprehensive mode - all files)...")
        
        ml_data = {}
        
        try:
            # ===== CORRELATION DATA =====
            # Main correlation with target
            corr_file = self.ml_data_path / "02_correlation_with_target.csv"
            if corr_file.exists():
                ml_data['correlation'] = pd.read_csv(corr_file)
                logger.info(f"Loaded correlation data: {len(ml_data['correlation'])} variables")
            
            # Long calls correlation
            corr_long_file = self.ml_data_path / "02_correlation_long_calls.csv"
            if corr_long_file.exists():
                ml_data['correlation_long_calls'] = pd.read_csv(corr_long_file)
                logger.info(f"Loaded long calls correlation: {len(ml_data['correlation_long_calls'])} variables")
            
            # Short calls correlation
            corr_short_file = self.ml_data_path / "02_correlation_short_calls.csv"
            if corr_short_file.exists():
                ml_data['correlation_short_calls'] = pd.read_csv(corr_short_file)
                logger.info(f"Loaded short calls correlation: {len(ml_data['correlation_short_calls'])} variables")
            
            # ===== FEATURE IMPORTANCE DATA =====
            # Combined importance
            importance_file = self.ml_data_path / "03_importance_combined.csv"
            if importance_file.exists():
                ml_data['importance'] = pd.read_csv(importance_file)
                logger.info(f"Loaded combined feature importance: {len(ml_data['importance'])} variables")
            
            # Random Forest importance
            importance_rf_file = self.ml_data_path / "03_importance_random_forest.csv"
            if importance_rf_file.exists():
                ml_data['importance_rf'] = pd.read_csv(importance_rf_file)
                logger.info(f"Loaded Random Forest importance: {len(ml_data['importance_rf'])} variables")
            
            # XGBoost importance
            importance_xgb_file = self.ml_data_path / "03_importance_xgboost.csv"
            if importance_xgb_file.exists():
                ml_data['importance_xgb'] = pd.read_csv(importance_xgb_file)
                logger.info(f"Loaded XGBoost importance: {len(ml_data['importance_xgb'])} variables")
            
            # ===== SHAP DATA =====
            shap_file = self.ml_data_path / "05_shap_importance.csv"
            if shap_file.exists():
                ml_data['shap'] = pd.read_csv(shap_file)
                logger.info(f"Loaded SHAP data: {len(ml_data['shap'])} variables")
            
            # ===== STATISTICAL TESTS DATA =====
            # Numerical tests
            stat_num_file = self.ml_data_path / "04_statistical_tests_numerical.csv"
            if stat_num_file.exists():
                ml_data['statistical_numerical'] = pd.read_csv(stat_num_file)
                logger.info(f"Loaded numerical statistical tests: {len(ml_data['statistical_numerical'])} variables")
            
            # Categorical tests
            stat_cat_file = self.ml_data_path / "04_statistical_tests_categorical.csv"
            if stat_cat_file.exists():
                ml_data['statistical_categorical'] = pd.read_csv(stat_cat_file)
                logger.info(f"Loaded categorical statistical tests: {len(ml_data['statistical_categorical'])} variables")
            
            # Combined statistical tests
            stat_combined_file = self.ml_data_path / "04_statistical_tests_combined.csv"
            if stat_combined_file.exists():
                ml_data['statistical'] = pd.read_csv(stat_combined_file)
                logger.info(f"Loaded combined statistical tests: {len(ml_data['statistical'])} variables")
            elif stat_num_file.exists() and stat_cat_file.exists():
                # Fallback: combine if combined file doesn't exist
                stat_num = pd.read_csv(stat_num_file)
                stat_cat = pd.read_csv(stat_cat_file)
                ml_data['statistical'] = pd.concat([stat_num, stat_cat], ignore_index=True)
                logger.info(f"Combined statistical tests: {len(ml_data['statistical'])} variables")
            
            # ===== LIME DATA =====
            lime_file = self.ml_data_path / "05b_lime_importance.csv"
            if lime_file.exists():
                ml_data['lime'] = pd.read_csv(lime_file)
                logger.info(f"Loaded LIME data: {len(ml_data['lime'])} variables")
            
            # LIME summary JSON
            lime_summary_file = self.ml_data_path / "05b_lime_summary.json"
            if lime_summary_file.exists():
                with open(lime_summary_file, 'r') as f:
                    ml_data['lime_summary'] = json.load(f)
                logger.info("Loaded LIME summary JSON")
            
            # ===== METADATA & METRICS =====
            # Metadata
            metadata_file = self.ml_data_path / "01_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    ml_data['metadata'] = json.load(f)
                logger.info("Loaded metadata")
            
            # Model metrics
            metrics_file = self.ml_data_path / "03_model_metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    ml_data['model_metrics'] = json.load(f)
                logger.info("Loaded model metrics")
            
            # ===== ORIGINAL DATA (for context) =====
            # Missing values summary
            missing_file = self.ml_data_path / "01_missing_values_summary.csv"
            if missing_file.exists():
                ml_data['missing_values'] = pd.read_csv(missing_file)
                logger.info(f"Loaded missing values summary: {len(ml_data['missing_values'])} variables")
            
            logger.info(f"Comprehensive ML data loading complete: {len(ml_data)} data sources loaded")
            
        except Exception as e:
            logger.error(f"Error loading ML data: {str(e)}")
        
        return ml_data
    
    def _analyze_correlations(self, corr_df: Optional[pd.DataFrame], ml_data: Dict = None) -> List[MLInsight]:
        """
        REASONING: Analyze correlation patterns (enhanced with long/short call data)
        
        Args:
            corr_df: Correlation dataframe
            ml_data: Full ML data dictionary for additional context
            
        Returns:
            List of correlation insights
        """
        insights = []
        
        if corr_df is None or corr_df.empty:
            return insights
        
        try:
            # Check if required columns exist
            required_cols = ['Variable', 'Correlation', 'Abs_Correlation', 'P_Value', 'Direction']
            if not all(col in corr_df.columns for col in required_cols):
                logger.warning(f"Correlation dataframe missing required columns. Has: {corr_df.columns.tolist()}")
                return insights
            
            # Top positive correlations
            top_positive = corr_df[corr_df['Direction'] == 'Positive'].nlargest(5, 'Abs_Correlation')
            
            for _, row in top_positive.iterrows():
                # Check if we have long/short call specific data
                additional_context = ""
                if ml_data:
                    if 'correlation_long_calls' in ml_data and 'correlation_short_calls' in ml_data:
                        try:
                            var_name = row['Variable']
                            long_corr = ml_data['correlation_long_calls']
                            short_corr = ml_data['correlation_short_calls']
                            
                            # Find this variable in long/short correlations
                            long_match = long_corr[long_corr['Variable'] == var_name]
                            short_match = short_corr[short_corr['Variable'] == var_name]
                            
                            if not long_match.empty and not short_match.empty:
                                long_val = long_match.iloc[0].get('Correlation', 0)
                                short_val = short_match.iloc[0].get('Correlation', 0)
                                additional_context = f" | Long calls: {long_val:.3f}, Short calls: {short_val:.3f}"
                        except Exception as e:
                            logger.debug(f"Could not add long/short context for {var_name}: {str(e)}")
                
                insights.append(MLInsight(
                    category="correlation",
                    insight=f"{row['Variable']} shows strong positive correlation with call duration",
                    evidence=f"Correlation: {row['Correlation']:.3f}, p-value: {row['P_Value']:.4f}{additional_context}",
                    recommendation=f"Focus on optimizing {row['Variable']} to increase call duration",
                    importance_score=float(row['Abs_Correlation']),
                    visualization_path="ML V2/analysis_outputs/level1_variable/heatmap_02_combined.png"
                ))
            
            # Top negative correlations
            top_negative = corr_df[corr_df['Direction'] == 'Negative'].nlargest(5, 'Abs_Correlation')
            
            for _, row in top_negative.iterrows():
                insights.append(MLInsight(
                    category="correlation",
                    insight=f"{row['Variable']} shows strong negative correlation with call duration",
                    evidence=f"Correlation: {row['Correlation']:.3f}, p-value: {row['P_Value']:.4f}",
                    recommendation=f"Investigate why {row['Variable']} reduces call duration",
                    importance_score=float(row['Abs_Correlation']),
                    visualization_path="ML V2/analysis_outputs/level1_variable/heatmap_02_combined.png"
                ))
            
            logger.info(f"Generated {len(insights)} correlation insights")
            
        except Exception as e:
            logger.error(f"Error analyzing correlations: {str(e)}")
        
        return insights
    
    def _analyze_feature_importance(self, importance_df: Optional[pd.DataFrame]) -> List[MLInsight]:
        """
        REASONING: Analyze feature importance from ML models
        
        Args:
            importance_df: Feature importance dataframe
            
        Returns:
            List of feature importance insights
        """
        insights = []
        
        if importance_df is None or importance_df.empty:
            return insights
        
        try:
            # Top 10 most important features
            top_features = importance_df.nlargest(10, 'Combined_Score')
            
            for idx, row in top_features.iterrows():
                insights.append(MLInsight(
                    category="feature_importance",
                    insight=f"{row['Variable']} is a critical predictor of call duration (Rank #{idx+1})",
                    evidence=f"Combined Score: {row['Combined_Score']:.4f}, RF: {row['RF_Importance']:.4f}, XGB: {row['XGB_Importance']:.4f}",
                    recommendation=f"Prioritize monitoring and optimizing {row['Variable']} in agent training",
                    importance_score=float(row['Combined_Score']),
                    visualization_path="ML V2/analysis_outputs/level1_variable/viz_06_top_20_variables.png"
                ))
            
            logger.info(f"Generated {len(insights)} feature importance insights")
            
        except Exception as e:
            logger.error(f"Error analyzing feature importance: {str(e)}")
        
        return insights
    
    def _analyze_shap(self, shap_df: Optional[pd.DataFrame]) -> List[MLInsight]:
        """
        REASONING: Analyze SHAP values for explainability
        
        Args:
            shap_df: SHAP importance dataframe
            
        Returns:
            List of SHAP insights
        """
        insights = []
        
        if shap_df is None or shap_df.empty:
            return insights
        
        try:
            # Top SHAP contributors
            top_shap = shap_df.nlargest(10, 'SHAP_Avg')
            
            for idx, row in top_shap.iterrows():
                insights.append(MLInsight(
                    category="shap",
                    insight=f"{row['Variable']} has high SHAP impact on predictions",
                    evidence=f"SHAP Avg: {row['SHAP_Avg']:.4f}, RF: {row['SHAP_RF']:.4f}, XGB: {row['SHAP_XGB']:.4f}",
                    recommendation=f"Analyze specific values of {row['Variable']} that push calls toward long/short duration",
                    importance_score=float(row['SHAP_Avg']),
                    visualization_path="ML V2/analysis_outputs/level1_variable/shap_05_rf_waterfall.png"
                ))
            
            logger.info(f"Generated {len(insights)} SHAP insights")
            
        except Exception as e:
            logger.error(f"Error analyzing SHAP: {str(e)}")
        
        return insights
    
    def _analyze_statistical_tests(self, stat_df: Optional[pd.DataFrame]) -> List[MLInsight]:
        """
        REASONING: Analyze statistical significance
        
        Args:
            stat_df: Statistical tests dataframe
            
        Returns:
            List of statistical insights
        """
        insights = []
        
        if stat_df is None or stat_df.empty:
            return insights
        
        try:
            # Filter for significant results
            if 'Significant_MW' in stat_df.columns:
                significant = stat_df[stat_df['Significant_MW'] == 'Yes']
            elif 'Significant' in stat_df.columns:
                significant = stat_df[stat_df['Significant'] == 'Yes']
            else:
                significant = stat_df
            
            # Top by effect size
            if 'Abs_Cohens_D' in significant.columns:
                top_effect = significant.nlargest(5, 'Abs_Cohens_D')
                
                for _, row in top_effect.iterrows():
                    insights.append(MLInsight(
                        category="statistical",
                        insight=f"{row['Variable']} shows statistically significant difference between short/long calls",
                        evidence=f"Cohen's D: {row['Abs_Cohens_D']:.3f}, p-value: {row.get('Mann_Whitney_PValue', row.get('T_PValue', 0)):.4f}",
                        recommendation=f"Target {row['Variable']} for intervention - it has measurable impact",
                        importance_score=float(row['Abs_Cohens_D']),
                        visualization_path="ML V2/analysis_outputs/level1_variable/viz_06_effect_sizes.png"
                    ))
            
            logger.info(f"Generated {len(insights)} statistical insights")
            
        except Exception as e:
            logger.error(f"Error analyzing statistical tests: {str(e)}")
        
        return insights
    
    def _analyze_lime(self, lime_df: Optional[pd.DataFrame]) -> List[MLInsight]:
        """
        REASONING: Analyze LIME explanations
        
        Args:
            lime_df: LIME importance dataframe
            
        Returns:
            List of LIME insights
        """
        insights = []
        
        if lime_df is None or lime_df.empty:
            return insights
        
        try:
            # Top LIME features
            top_lime = lime_df.nlargest(5, 'LIME_Avg')
            
            for _, row in top_lime.iterrows():
                insights.append(MLInsight(
                    category="lime",
                    insight=f"{row['Variable']} is locally important for individual predictions",
                    evidence=f"LIME Avg: {row['LIME_Avg']:.4f}, RF: {row['LIME_RF']:.4f}, XGB: {row['LIME_XGB']:.4f}",
                    recommendation=f"Use {row['Variable']} for personalized agent coaching",
                    importance_score=float(row['LIME_Avg']),
                    visualization_path="ML V2/analysis_outputs/level1_variable/lime_05b_aggregated_importance.png"
                ))
            
            logger.info(f"Generated {len(insights)} LIME insights")
            
        except Exception as e:
            logger.error(f"Error analyzing LIME: {str(e)}")
        
        return insights
    
    def _synthesize_insights(self, all_insights: List[MLInsight], ml_data: Dict) -> MLInsightsCollection:
        """
        ACTING: Synthesize all insights using LLM
        
        Args:
            all_insights: All individual insights
            ml_data: Raw ML data
            
        Returns:
            Comprehensive insights collection
        """
        logger.info("Synthesizing insights with LLM...")
        
        try:
            # Get top variables from multiple sources
            top_vars = self._get_top_variables(ml_data)
            
            # Sort insights by importance
            all_insights.sort(key=lambda x: x.importance_score, reverse=True)
            
            # Take top 20 insights
            key_insights = all_insights[:20]
            
            # Generate statistical summary
            stat_summary = self._generate_statistical_summary(ml_data)
            
            # Generate recommendations using LLM
            recommendations = self._generate_recommendations_with_llm(key_insights, ml_data)
            
            # Select visualizations to include
            visualizations = self._select_key_visualizations()
            
            # Generate section-specific insights for organic blending
            agent_perf_insights = self._generate_agent_performance_insights(ml_data, all_insights)
            call_pattern_insights = self._generate_call_pattern_insights(ml_data, all_insights)
            lead_quality_insights = self._generate_lead_quality_insights(ml_data, all_insights)
            lgs_omc_insights = self._generate_lgs_omc_insights(ml_data, all_insights)
            rec_insights = self._generate_recommendations_insights(ml_data, all_insights)
            
            return MLInsightsCollection(
                top_variables=top_vars,
                key_insights=key_insights,
                statistical_summary=stat_summary,
                recommendations_summary=recommendations,
                visualizations_to_include=visualizations,
                agent_performance_insights=agent_perf_insights,
                call_pattern_insights=call_pattern_insights,
                lead_quality_insights=lead_quality_insights,
                lgs_omc_insights=lgs_omc_insights,
                recommendations_insights=rec_insights
            )
            
        except Exception as e:
            logger.error(f"Error synthesizing insights: {str(e)}")
            return self._create_empty_insights()
    
    def _get_top_variables(self, ml_data: Dict) -> List[str]:
        """Get top 10 variables from combined analysis"""
        try:
            if 'importance' in ml_data:
                return ml_data['importance'].nlargest(10, 'Combined_Score')['Variable'].tolist()
            elif 'shap' in ml_data:
                return ml_data['shap'].nlargest(10, 'SHAP_Avg')['Variable'].tolist()
            else:
                return []
        except:
            return []
    
    def _generate_statistical_summary(self, ml_data: Dict) -> str:
        """Generate statistical summary"""
        try:
            summary_parts = []
            
            if 'metadata' in ml_data:
                meta = ml_data['metadata']
                summary_parts.append(f"Analyzed {meta.get('total_variables', 'N/A')} variables across {meta.get('total_records', 'N/A')} calls")
            
            if 'model_metrics' in ml_data:
                metrics = ml_data['model_metrics']
                summary_parts.append(f"Random Forest ROC-AUC: {metrics.get('random_forest_roc_auc_test', 0):.3f}")
                summary_parts.append(f"XGBoost ROC-AUC: {metrics.get('xgboost_roc_auc_test', 0):.3f}")
            
            if 'statistical' in ml_data:
                sig_count = len(ml_data['statistical'][ml_data['statistical'].get('Significant_MW', ml_data['statistical'].get('Significant', pd.Series([False]))).isin(['Yes', True])])
                summary_parts.append(f"{sig_count} variables show statistically significant differences")
            
            return " | ".join(summary_parts) if summary_parts else "No statistical summary available"
            
        except Exception as e:
            logger.error(f"Error generating statistical summary: {str(e)}")
            return "Statistical summary unavailable"
    
    def _generate_recommendations_with_llm(self, insights: List[MLInsight], ml_data: Dict) -> str:
        """Generate comprehensive recommendations using LLM"""
        try:
            # Prepare insights summary for LLM
            insights_text = "\n".join([
                f"- {insight.insight} ({insight.category}): {insight.recommendation}"
                for insight in insights[:15]
            ])
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a senior business analyst specializing in call center optimization.
                
Based on ML analysis insights, generate 5-7 actionable recommendations for improving call duration and conversion rates.

Focus on:
1. High-impact variables that can be controlled/trained
2. Specific, measurable actions
3. Priority order (most impactful first)
4. Practical implementation steps

Be concise and actionable."""),
                ("human", f"""ML Analysis Insights:

{insights_text}

Generate comprehensive recommendations:""")
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({})
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return "Recommendations unavailable - see individual insights for guidance"
    
    def _select_key_visualizations(self) -> List[str]:
        """Select ALL visualizations to include in report (comprehensive analysis)"""
        visualizations = []
        
        # Get ALL PNG files from the ML data directory
        try:
            if self.ml_data_path.exists():
                all_png_files = sorted(self.ml_data_path.glob("*.png"))
                
                # Priority order for better organization
                priority_order = [
                    "shap_05_rf_waterfall.png",  # SHAP waterfall (user requested)
                    "viz_06_top_20_variables.png",  # Feature importance (user requested)
                    "shap_05_rf_summary_beeswarm.png",  # SHAP summary
                    "viz_06_correlation_vs_importance.png",  # Correlation vs importance
                    "viz_06_effect_sizes.png",  # Effect sizes
                    "03_eval_roc_curves.png",  # Model performance
                    "03_eval_confusion_matrices.png",  # Confusion matrices
                    "03_eval_learning_curves.png",  # Learning curves
                    "03_eval_metrics_comparison.png",  # Metrics comparison
                    "heatmap_02_long_calls.png",  # Long calls correlation heatmap
                    "heatmap_02_short_calls.png",  # Short calls correlation heatmap
                    "shap_05_xgb_waterfall.png",  # XGBoost SHAP waterfall
                    "shap_05_xgb_summary_beeswarm.png",  # XGBoost SHAP summary
                    "shap_05_rf_importance_bar.png",  # RF SHAP importance
                    "shap_05_xgb_importance_bar.png",  # XGBoost SHAP importance
                    "shap_05_rf_dependence.png",  # RF SHAP dependence
                    "shap_05_xgb_dependence.png",  # XGBoost SHAP dependence
                    "lime_05b_aggregated_importance.png",  # LIME aggregated
                    "lime_05b_rf_individual_explanations.png",  # LIME RF explanations
                    "lime_05b_gb_individual_explanations.png",  # LIME GB explanations
                    "lime_05b_lime_vs_shap.png",  # LIME vs SHAP comparison
                    "04_stat_effect_vs_pvalue.png",  # Effect vs p-value
                    "04_stat_mean_differences.png",  # Mean differences
                    "04_stat_pvalue_distributions.png",  # P-value distributions
                    "04_stat_significance_summary.png",  # Significance summary
                    "viz_06_model_comparison.png",  # Model comparison
                    "viz_06_section_analysis.png"  # Section analysis
                ]
                
                # Add priority files first (if they exist)
                for priority_file in priority_order:
                    viz_path = self.ml_data_path / priority_file
                    if viz_path.exists():
                        visualizations.append(str(viz_path))
                
                # Add any remaining PNG files not in priority list
                for png_file in all_png_files:
                    viz_path_str = str(png_file)
                    if viz_path_str not in visualizations:
                        visualizations.append(viz_path_str)
                
                logger.info(f"Selected {len(visualizations)} visualizations for comprehensive analysis")
            else:
                logger.warning(f"ML data path does not exist: {self.ml_data_path}")
        
        except Exception as e:
            logger.error(f"Error selecting visualizations: {str(e)}")
        
        return visualizations
    
    def _generate_agent_performance_insights(self, ml_data: Dict, all_insights: List[MLInsight]) -> Dict:
        """Generate ML insights specific to agent performance section"""
        insights = {
            'discovery_questions_impact': None,
            'buying_signals_impact': None,
            'objection_handling_impact': None,
            'visualization_path': None
        }
        
        try:
            # Find insights related to agent behavior
            for insight in all_insights:
                if 'discovery_questions' in insight.insight.lower():
                    insights['discovery_questions_impact'] = {
                        'insight': insight.insight,
                        'evidence': insight.evidence,
                        'score': insight.importance_score
                    }
                elif 'buying_signals' in insight.insight.lower():
                    insights['buying_signals_impact'] = {
                        'insight': insight.insight,
                        'evidence': insight.evidence,
                        'score': insight.importance_score
                    }
                elif 'objection' in insight.insight.lower():
                    insights['objection_handling_impact'] = {
                        'insight': insight.insight,
                        'evidence': insight.evidence,
                        'score': insight.importance_score
                    }
            
            # Add relevant visualization
            for viz_path in self._select_key_visualizations():
                if 'top_20' in viz_path or 'waterfall' in viz_path:
                    insights['visualization_path'] = viz_path
                    break
                    
        except Exception as e:
            logger.error(f"Error generating agent performance insights: {str(e)}")
        
        return insights
    
    def _generate_call_pattern_insights(self, ml_data: Dict, all_insights: List[MLInsight]) -> Dict:
        """Generate ML insights specific to call pattern section"""
        insights = {
            'short_call_predictors': [],
            'long_call_predictors': [],
            'visualization_path': None
        }
        
        try:
            # Get correlation data for call duration
            if 'correlation' in ml_data:
                corr_df = ml_data['correlation']
                
                # Negative correlations (predict short calls)
                negative_corr = corr_df[corr_df['Direction'] == 'Negative'].nlargest(3, 'Abs_Correlation')
                for _, row in negative_corr.iterrows():
                    insights['short_call_predictors'].append({
                        'variable': row['Variable'],
                        'correlation': float(row['Correlation']),
                        'evidence': f"Correlation: {row['Correlation']:.3f}, p-value: {row['P_Value']:.4f}"
                    })
                
                # Positive correlations (predict long calls)
                positive_corr = corr_df[corr_df['Direction'] == 'Positive'].nlargest(3, 'Abs_Correlation')
                for _, row in positive_corr.iterrows():
                    insights['long_call_predictors'].append({
                        'variable': row['Variable'],
                        'correlation': float(row['Correlation']),
                        'evidence': f"Correlation: {row['Correlation']:.3f}, p-value: {row['P_Value']:.4f}"
                    })
            
            # Add relevant visualization
            for viz_path in self._select_key_visualizations():
                if 'effect_sizes' in viz_path or 'beeswarm' in viz_path:
                    insights['visualization_path'] = viz_path
                    break
                    
        except Exception as e:
            logger.error(f"Error generating call pattern insights: {str(e)}")
        
        return insights
    
    def _generate_lead_quality_insights(self, ml_data: Dict, all_insights: List[MLInsight]) -> Dict:
        """Generate ML insights specific to lead quality section"""
        insights = {
            'lead_quality_variables': [],
            'visualization_path': None
        }
        
        try:
            # Find LQ_ (Lead Quality) related insights
            for insight in all_insights:
                if 'LQ_' in insight.insight or 'lead' in insight.insight.lower():
                    insights['lead_quality_variables'].append({
                        'insight': insight.insight,
                        'evidence': insight.evidence,
                        'recommendation': insight.recommendation,
                        'score': insight.importance_score
                    })
            
            # Add relevant visualization
            for viz_path in self._select_key_visualizations():
                if 'correlation' in viz_path:
                    insights['visualization_path'] = viz_path
                    break
                    
        except Exception as e:
            logger.error(f"Error generating lead quality insights: {str(e)}")
        
        return insights
    
    def _generate_lgs_omc_insights(self, ml_data: Dict, all_insights: List[MLInsight]) -> Dict:
        """Generate ML insights specific to LGS/OMC handoff section"""
        insights = {
            'handoff_quality_indicators': [],
            'visualization_path': None
        }
        
        try:
            # Find handoff-related variables
            for insight in all_insights:
                if any(keyword in insight.insight.lower() for keyword in ['lgs', 'omc', 'transfer', 'handoff', 'consent']):
                    insights['handoff_quality_indicators'].append({
                        'insight': insight.insight,
                        'evidence': insight.evidence,
                        'score': insight.importance_score
                    })
            
        except Exception as e:
            logger.error(f"Error generating LGS/OMC insights: {str(e)}")
        
        return insights
    
    def _generate_recommendations_insights(self, ml_data: Dict, all_insights: List[MLInsight]) -> Dict:
        """Generate ML insights for recommendations section"""
        insights = {
            'high_impact_variables': [],
            'trainable_variables': [],
            'visualization_path': None
        }
        
        try:
            # Get top importance variables
            if 'importance' in ml_data:
                top_importance = ml_data['importance'].nlargest(5, 'Combined_Score')
                
                for _, row in top_importance.iterrows():
                    var_name = row['Variable']
                    
                    # Categorize as trainable or not
                    trainable_keywords = ['discovery', 'objection', 'buying_signal', 'talk_percentage', 'question']
                    is_trainable = any(keyword in var_name.lower() for keyword in trainable_keywords)
                    
                    insight_dict = {
                        'variable': var_name,
                        'score': float(row['Combined_Score']),
                        'evidence': f"RF: {row['RF_Importance']:.4f}, XGB: {row['XGB_Importance']:.4f}"
                    }
                    
                    if is_trainable:
                        insights['trainable_variables'].append(insight_dict)
                    else:
                        insights['high_impact_variables'].append(insight_dict)
            
            # Add ROC curve visualization
            for viz_path in self._select_key_visualizations():
                if 'roc' in viz_path:
                    insights['visualization_path'] = viz_path
                    break
                    
        except Exception as e:
            logger.error(f"Error generating recommendations insights: {str(e)}")
        
        return insights
    
    def _create_empty_insights(self) -> MLInsightsCollection:
        """Create empty insights collection when ML data is unavailable"""
        return MLInsightsCollection(
            top_variables=[],
            key_insights=[],
            statistical_summary="ML analysis data not available",
            recommendations_summary="Run ML analysis scripts to generate insights",
            visualizations_to_include=[],
            agent_performance_insights={},
            call_pattern_insights={},
            lead_quality_insights={},
            lgs_omc_insights={},
            recommendations_insights={}
        )

