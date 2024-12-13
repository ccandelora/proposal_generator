"""Proposal generation workflow."""
from typing import Dict, Any, List, Set, Optional, Callable
import logging
from ..config import Config
from ..components.search.google_search import GoogleSearchClient
from ..components.search.search_results_manager import SearchResultsManager
from ..components.content_generator.agents.topic_agent import TopicAnalyzerAgent
from ..components.content_generator.agents.writing_agent import WritingAgent
from ..components.content_generator.agents.style_agent import StyleGuideAgent
from ..components.seo_analyzer.agents.content_agent import ContentSEOAgent
from ..components.seo_screenshotter.main import SEOScreenshotter
from ..components.export_manager import ExportManager
from ..models.content_model import ContentRequest, ContentType, ContentTone
from ..utils.text_processor import clean_text, extract_sentences
import re
from collections import Counter
import spacy
from textblob import TextBlob
from ..utils.progress_visualizer import ProgressVisualizer
from ..utils.web_progress_tracker import WebProgressTracker

logger = logging.getLogger(__name__)

class WorkflowStage:
    """Enum-like class for workflow stages."""
    RESEARCH = "Research"
    TOPIC_ANALYSIS = "Topic Analysis"
    CONTENT_GENERATION = "Content Generation"
    STYLE_APPLICATION = "Style Application"
    FINAL_COMPILATION = "Final Compilation"

class ProposalWorkflowManager:
    """Main workflow for proposal generation."""
    
    def __init__(self, config: Config, progress_callback: Optional[Callable] = None, web_progress: bool = False):
        """Initialize workflow."""
        self.config = config
        
        # Initialize progress tracking
        self.web_tracker = WebProgressTracker() if web_progress else None
        self.terminal_visualizer = ProgressVisualizer() if not web_progress else None
        
        # Set up progress callback
        self.progress_callback = progress_callback or (
            self.web_tracker.update if web_progress else 
            self.terminal_visualizer.update if self.terminal_visualizer else None
        )
        
        # Initialize workflow state
        self.current_stage = None
        self.completed_steps = []
        self.overall_progress = 0
        
        # Initialize NLP
        try:
            # Use medium-sized model with word vectors
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            # If model is not installed, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"])
            self.nlp = spacy.load("en_core_web_md")
        
        # Initialize components with progress tracking
        self.search_client = GoogleSearchClient(
            config,
            progress_callback=self._component_progress
        )
        self.search_manager = SearchResultsManager(
            self.search_client, 
            progress_callback=self._component_progress
        )
        
        # Initialize agents with progress tracking
        self.topic_agent = TopicAnalyzerAgent(
            progress_callback=self._agent_progress
        )
        self.writing_agent = WritingAgent(
            progress_callback=self._agent_progress
        )
        self.style_agent = StyleGuideAgent(
            progress_callback=self._agent_progress
        )
        
        # Initialize SEO components
        self.seo_agent = ContentSEOAgent(
            progress_callback=self._component_progress
        )
        self.screenshotter = SEOScreenshotter(
            progress_callback=self._component_progress
        )
        
        # Initialize export manager
        self.export_manager = ExportManager(
            output_dir="exports",
            progress_callback=self._component_progress
        )

    def _component_progress(self, component: str, message: str, progress: int):
        """Handle progress updates from components."""
        if self.progress_callback:
            stage_message = f"{component}: {message}"
            self.progress_callback(stage_message, progress, self.completed_steps)

    def _agent_progress(self, message: str, progress: int):
        """Handle progress updates from agents."""
        if self.current_stage and self.progress_callback:
            self.progress_callback(
                f"{self.current_stage}: {message}",
                progress,
                self.completed_steps
            )

    async def _update_progress(self, stage: str, progress: int, message: str = ""):
        """Update overall workflow progress."""
        if self.progress_callback:
            self.current_stage = stage
            
            # Calculate overall progress
            stage_weights = {
                WorkflowStage.RESEARCH: 0.25,
                WorkflowStage.TOPIC_ANALYSIS: 0.15,
                WorkflowStage.CONTENT_GENERATION: 0.35,
                WorkflowStage.STYLE_APPLICATION: 0.15,
                WorkflowStage.FINAL_COMPILATION: 0.10
            }
            
            # Calculate weighted progress
            stage_progress = {
                s: 100 if s in self.completed_steps else 0 
                for s in stage_weights
            }
            stage_progress[stage] = progress
            
            self.overall_progress = sum(
                stage_progress[s] * weight 
                for s, weight in stage_weights.items()
            )
            
            # Update progress trackers
            status = f"{stage}: {message}" if message else stage
            
            if self.web_tracker:
                await self.web_tracker.update(status, self.overall_progress, self.completed_steps)
            elif self.terminal_visualizer:
                self.terminal_visualizer.update(status, self.overall_progress, self.completed_steps)

    async def generate_proposal(self, topic: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proposal based on topic and requirements."""
        try:
            # Step 1: Research phase
            await self._update_progress(WorkflowStage.RESEARCH, 0, "Starting research...")
            search_results = await self._perform_research(topic)
            self.completed_steps.append(WorkflowStage.RESEARCH)
            
            # Step 2: Topic analysis
            await self._update_progress(WorkflowStage.TOPIC_ANALYSIS, 0, "Analyzing topic...")
            content_request = self._create_content_request(topic, requirements)
            topic_analysis = self.topic_agent.analyze_topic(content_request)
            self.completed_steps.append(WorkflowStage.TOPIC_ANALYSIS)
            
            # Step 3: Content generation
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 0, "Generating content...")
            content = await self._generate_content(
                content_request,
                topic_analysis,
                search_results
            )
            self.completed_steps.append(WorkflowStage.CONTENT_GENERATION)
            
            # Step 4: Style application
            await self._update_progress(WorkflowStage.STYLE_APPLICATION, 0, "Applying style...")
            # Get the full content from sections
            full_content = "\n\n".join([
                f"# {section.title}\n{section.content}"
                for section in content.sections
            ])
            styled_content = self.style_agent.apply_style_rules(
                full_content,  # Use the combined content
                content_request.tone
            )
            self.completed_steps.append(WorkflowStage.STYLE_APPLICATION)
            
            # Final compilation
            await self._update_progress(WorkflowStage.FINAL_COMPILATION, 0, "Compiling final document...")
            result = {
                'content': styled_content,
                'metadata': {
                    'topic_analysis': topic_analysis,
                    'research_sources': [r['url'] for r in search_results[:5]],
                    'content_metrics': content.metrics
                }
            }
            self.completed_steps.append(WorkflowStage.FINAL_COMPILATION)
            await self._update_progress(WorkflowStage.FINAL_COMPILATION, 100, "Proposal complete")
            
            self.terminal_visualizer.complete()
            return result
            
        except Exception as e:
            logger.error(f"Error in proposal workflow: {str(e)}")
            await self._update_progress(self.current_stage, 0, f"Error: {str(e)}")
            self.terminal_visualizer.error(str(e))
            raise

    async def _perform_research(self, topic: str) -> List[Dict[str, Any]]:
        """Perform research using search functionality."""
        try:
            # Generate search queries
            await self._update_progress(WorkflowStage.RESEARCH, 10, "Generating search queries...")
            queries = self._generate_search_queries(topic)
            logger.info(f"Generated search queries: {queries}")  # Add logging
            all_results = []
            
            # Perform searches
            total_queries = len(queries)
            for i, query in enumerate(queries, 1):
                progress = int((i / total_queries) * 80) + 10  # 10-90% of research phase
                await self._update_progress(
                    WorkflowStage.RESEARCH, 
                    progress,
                    f"Searching ({i}/{total_queries}): {query}"
                )
                
                try:
                    # Add more detailed logging
                    logger.info(f"Executing search for query: {query}")
                    results = await self.search_manager.search_and_process(query, num_results=5)
                    logger.info(f"Found {len(results)} results for query: {query}")
                    
                    all_results.extend([{
                        'url': r.url,
                        'title': r.title,
                        'content': r.content,
                        'relevance': r.relevance_score
                    } for r in results])
                    
                except Exception as e:
                    logger.error(f"Error searching for query '{query}': {str(e)}")
                    continue
            
            # Process and sort results
            await self._update_progress(WorkflowStage.RESEARCH, 90, "Processing search results...")
            all_results.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Add result summary logging
            logger.info(f"Research complete. Found {len(all_results)} total results")
            if all_results:
                logger.info("Top 3 most relevant results:")
                for i, r in enumerate(all_results[:3], 1):
                    logger.info(f"{i}. {r['title']} (relevance: {r['relevance']:.2f})")
            else:
                logger.warning("No research results found!")
            
            await self._update_progress(
                WorkflowStage.RESEARCH, 
                100, 
                f"Found {len(all_results)} relevant results"
            )
            return all_results
            
        except Exception as e:
            logger.error(f"Error in research phase: {str(e)}")
            raise

    def _create_content_request(self, topic: str, requirements: Dict[str, Any]) -> ContentRequest:
        """Create content request from requirements."""
        return ContentRequest(
            content_type=ContentType.PROPOSAL,
            topic=topic,
            target_audience=requirements.get('target_audience', ''),
            tone=ContentTone.PROFESSIONAL,
            key_points=requirements.get('features', []),
            keywords=requirements.get('keywords', []),
            max_length=requirements.get('max_length', 5000),
            required_sections=[
                'Executive Summary',
                'Project Overview',
                'Solution Details',
                'Implementation Plan',
                'Timeline and Deliverables',
                'Investment'
            ],
            reference_data={
                'industry': requirements.get('industry', ''),
                'business_name': requirements.get('business_name', ''),
                'website': requirements.get('website', ''),
                'competitors': requirements.get('competitors', [])
            }
        )

    async def _generate_content(self, 
                              content_request: ContentRequest,
                              topic_analysis: Dict[str, Any],
                              research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate content using research results and agents."""
        try:
            # Enhance topic analysis with research
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 10, "Enhancing topic analysis with research...")
            enhanced_analysis = self._enhance_topic_analysis(
                topic_analysis,
                research_results
            )
            
            # Prepare content structure
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 20, "Preparing content structure...")
            
            # Generate content sections
            total_sections = len(enhanced_analysis['outline']['sections'])
            for i, section in enumerate(enhanced_analysis['outline']['sections'], 1):
                progress = 20 + int((i / total_sections) * 60)  # 20-80% progress
                await self._update_progress(
                    WorkflowStage.CONTENT_GENERATION,
                    progress,
                    f"Generating section {i}/{total_sections}: {section['name']}"
                )
            
            # Generate content using writing agent
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 80, "Finalizing content generation...")
            content = self.writing_agent.generate_content(
                content_request,
                enhanced_analysis
            )
            
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 90, "Reviewing generated content...")
            
            # Final content validation
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 95, "Validating content quality...")
            
            await self._update_progress(WorkflowStage.CONTENT_GENERATION, 100, "Content generation complete")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    def _enhance_topic_analysis(self, 
                              topic_analysis: Dict[str, Any],
                              research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance topic analysis with research findings."""
        enhanced = topic_analysis.copy()
        
        # Add research-based insights
        logger.info("Extracting key insights from research...")
        enhanced['research_insights'] = {
            'key_points': self._extract_key_points(research_results),
            'market_data': self._extract_market_data(research_results),
            'sources': [
                {
                    'url': r['url'],
                    'title': r['title'],
                    'relevance': r['relevance']
                }
                for r in research_results[:5]  # Top 5 most relevant sources
            ]
        }
        
        # Add themes from research
        logger.info("Analyzing research themes...")
        themes_from_research = self._extract_themes(research_results)
        enhanced['themes'].extend(themes_from_research)
        
        # Add detailed analysis
        logger.info("Generating detailed analysis...")
        enhanced['detailed_analysis'] = {
            'market_trends': self._analyze_market_trends(research_results),
            'competitive_landscape': self._analyze_competition(research_results),
            'key_opportunities': self._identify_opportunities(research_results)
        }
        
        return enhanced

    def _extract_themes(self, research_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract themes from research results using NLP."""
        try:
            themes = []
            all_noun_phrases = []
            
            for result in research_results:
                try:
                    content = clean_text(result.get('content', ''))
                    if not content:
                        continue
                    
                    doc = self.nlp(content[:10000])  # Limit content length to avoid memory issues
                    
                    # Extract noun phrases
                    noun_phrases = [
                        chunk.text.lower() for chunk in doc.noun_chunks 
                        if len(chunk.text.split()) > 1 and len(chunk.text) < 100
                    ]
                    all_noun_phrases.extend(noun_phrases)
                    
                    # Extract named entities
                    entities = [
                        (ent.text, ent.label_) for ent in doc.ents 
                        if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'TECH']
                    ]
                    
                    # Analyze sentiment for context
                    try:
                        blob = TextBlob(content)
                        sentiment = blob.sentiment.polarity
                    except Exception as e:
                        logger.warning(f"Error calculating sentiment: {str(e)}")
                        sentiment = 0.0
                    
                    # Group related terms
                    phrase_counter = Counter(noun_phrases)
                    top_phrases = phrase_counter.most_common(5)
                    
                    for phrase, count in top_phrases:
                        theme = {
                            'name': phrase,
                            'frequency': count,
                            'sentiment': sentiment,
                            'source_url': result.get('url', ''),
                            'related_entities': [
                                ent for ent, _ in entities 
                                if phrase in ent.lower() or ent.lower() in phrase
                            ],
                            'relevance': self._calculate_theme_relevance(phrase, content)
                        }
                        themes.append(theme)
                        
                except Exception as e:
                    logger.warning(f"Error processing result: {str(e)}")
                    continue
            
            # Deduplicate and merge related themes
            if themes:
                merged_themes = self._merge_related_themes(themes)
                return sorted(merged_themes, key=lambda x: x['relevance'], reverse=True)
            return []
            
        except Exception as e:
            logger.error(f"Error extracting themes: {str(e)}")
            return []

    def _extract_key_points(self, research_results: List[Dict[str, Any]]) -> List[str]:
        """Extract key points using NLP and heuristics."""
        key_points = set()
        
        for result in research_results:
            content = clean_text(result['content'])
            sentences = extract_sentences(content)
            
            for sentence in sentences:
                # Process sentence with spaCy
                doc = self.nlp(sentence)
                
                # Identify potential key points based on indicators
                if self._is_key_point(doc):
                    # Clean and normalize the sentence
                    point = self._normalize_key_point(doc)
                    if point:
                        key_points.add(point)
        
        return list(sorted(key_points, key=len))

    def _extract_market_data(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract market data using pattern matching and NLP."""
        market_data = {
            'trends': [],
            'statistics': [],
            'competitors': [],
            'market_size': [],
            'growth_rates': []
        }
        
        for result in research_results:
            content = clean_text(result['content'])
            doc = self.nlp(content)
            
            # Extract statistics and numbers
            statistics = self._extract_statistics(doc)
            market_data['statistics'].extend(statistics)
            
            # Extract trends
            trends = self._extract_trends(doc)
            market_data['trends'].extend(trends)
            
            # Extract competitor information
            competitors = self._extract_competitors(doc)
            market_data['competitors'].extend(competitors)
            
            # Extract market size information
            market_sizes = self._extract_market_size(doc)
            market_data['market_size'].extend(market_sizes)
            
            # Extract growth rates
            growth_rates = self._extract_growth_rates(doc)
            market_data['growth_rates'].extend(growth_rates)
        
        # Deduplicate and clean results
        return self._deduplicate_market_data(market_data)

    def _is_key_point(self, doc) -> bool:
        """Determine if a sentence contains a key point."""
        # Key point indicators
        indicators = [
            "key", "important", "significant", "essential", "crucial",
            "primary", "major", "critical", "fundamental", "core"
        ]
        
        # Check for indicator words
        if any(token.text.lower() in indicators for token in doc):
            return True
            
        # Check for bullet points or numbering
        if doc[0].text in ["-", "•", "*"] or doc[0].text[0].isdigit():
            return True
            
        # Check for strong subject-verb-object structure
        has_subject = False
        has_verb = False
        has_object = False
        
        for token in doc:
            if token.dep_ == "nsubj":
                has_subject = True
            elif token.pos_ == "VERB":
                has_verb = True
            elif token.dep_ in ["dobj", "pobj"]:
                has_object = True
                
        return has_subject and has_verb and has_object

    def _normalize_key_point(self, doc) -> str:
        """Normalize and clean a key point."""
        # Remove leading indicators
        text = doc.text
        text = re.sub(r'^[-•*\d.)\s]+', '', text)
        
        # Ensure it starts with a capital letter
        text = text.strip().capitalize()
        
        # Remove redundant phrases
        redundant = ["it is important to note that", "note that", "keep in mind that"]
        for phrase in redundant:
            text = re.sub(rf'{phrase}', '', text, flags=re.IGNORECASE)
        
        return text.strip()

    def _extract_statistics(self, doc) -> List[Dict[str, Any]]:
        """Extract statistical information from text."""
        statistics = []
        
        # Look for statistical indicators
        stat_indicators = [
            "percent", "percentage", "rate",
            "average", "median", "mean",
            "approximately", "estimated",
            "roughly", "about", "around"
        ]
        
        # Number and percentage patterns
        number_pattern = r'(\d+\.?\d*)'
        percentage_pattern = r'(\d+\.?\d*)%'
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Check if sentence contains statistical indicators
            if any(indicator in sent_text for indicator in stat_indicators):
                # Extract numbers and percentages
                numbers = re.findall(number_pattern, sent.text)
                percentages = re.findall(percentage_pattern, sent.text)
                
                if numbers or percentages:
                    statistic = {
                        'values': numbers + [f"{p}%" for p in percentages],
                        'context': sent.text,
                        'year': self._extract_year(sent),
                        'source': doc.user_data.get('source_url', ''),
                        'confidence': self._calculate_confidence(sent),
                        'type': self._determine_statistic_type(sent)
                    }
                    statistics.append(statistic)
        
        return statistics

    def _determine_statistic_type(self, sent) -> str:
        """Determine type of statistic mentioned."""
        type_indicators = {
            'demographic': ['age', 'gender', 'location', 'population'],
            'financial': ['revenue', 'cost', 'price', 'profit', 'margin'],
            'performance': ['speed', 'efficiency', 'productivity', 'output'],
            'usage': ['users', 'adoption', 'engagement', 'activity'],
            'market': ['share', 'penetration', 'distribution', 'reach']
        }
        
        sent_text = sent.text.lower()
        
        for stat_type, indicators in type_indicators.items():
            if any(indicator in sent_text for indicator in indicators):
                return stat_type
            
        return 'general'

    def _extract_trends(self, doc) -> List[Dict[str, Any]]:
        """Extract market trends."""
        trend_indicators = ["increasing", "growing", "rising", "emerging", "declining"]
        trends = []
        
        for sent in doc.sents:
            if any(indicator in sent.text.lower() for indicator in trend_indicators):
                trends.append({
                    'description': sent.text.strip(),
                    'sentiment': TextBlob(sent.text).sentiment.polarity
                })
        return trends

    def _get_entity_context(self, doc, ent, window=5) -> str:
        """Get the surrounding context of an entity."""
        start = max(0, ent.start - window)
        end = min(len(doc), ent.end + window)
        return doc[start:end].text

    def _deduplicate_market_data(self, market_data: Dict[str, List]) -> Dict[str, List]:
        """Remove duplicates from market data while preserving the best quality items."""
        deduped = {}
        for key, items in market_data.items():
            seen = set()
            unique_items = []
            
            for item in items:
                item_text = str(item).lower()
                if item_text not in seen:
                    seen.add(item_text)
                    unique_items.append(item)
                    
            deduped[key] = unique_items
        return deduped

    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate search queries based on topic and requirements."""
        base_queries = [
            f"{topic} best practices",
            f"{topic} industry leaders",
            f"{topic} case studies",
            f"{topic} market analysis",
            f"{topic} trends 2024"
        ]
        
        # Add industry-specific queries
        industry_queries = [
            f"{topic} industry statistics",
            f"{topic} market size",
            f"{topic} competitive analysis",
            f"{topic} success stories",
            f"{topic} industry benchmarks"
        ]
        
        # Add feature-specific queries
        feature_queries = [
            f"{topic} design examples",
            f"{topic} implementation guide",
            f"{topic} technology stack",
            f"{topic} performance metrics",
            f"{topic} user experience"
        ]
        
        # Combine all queries
        all_queries = base_queries + industry_queries + feature_queries
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in all_queries:
            if query not in seen:
                unique_queries.append(query)
                seen.add(query)
        
        return unique_queries[:10]  # Return top 10 most relevant queries

    def _extract_competitors(self, doc) -> List[Dict[str, Any]]:
        """Extract competitor information from text."""
        competitors = []
        
        # Look for competitor mentions
        competitor_indicators = [
            "competitor", "competition", "rival", "alternative",
            "similar", "other provider", "market leader"
        ]
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Check if sentence contains competitor indicators
            if any(indicator in sent_text for indicator in competitor_indicators):
                # Extract organization names
                orgs = [
                    ent.text for ent in sent.ents 
                    if ent.label_ == "ORG" and len(ent.text) > 3
                ]
                
                # Add competitor info
                for org in orgs:
                    competitor = {
                        'name': org,
                        'mention_context': sent.text,
                        'sentiment': TextBlob(sent.text).sentiment.polarity,
                        'source': doc.user_data.get('source_url', '')
                    }
                    
                    # Only add if not already present
                    if not any(c['name'] == org for c in competitors):
                        competitors.append(competitor)
        
        return competitors

    def _extract_market_size(self, doc) -> List[Dict[str, Any]]:
        """Extract market size information from text."""
        market_sizes = []
        
        # Look for market size indicators
        size_indicators = [
            "market size", "market value", "market worth",
            "industry size", "revenue", "market share",
            "billion", "million", "market cap"
        ]
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Check if sentence contains market size indicators
            if any(indicator in sent_text for indicator in size_indicators):
                # Extract numerical values
                numbers = [
                    ent.text for ent in sent.ents 
                    if ent.label_ in ["MONEY", "CARDINAL", "QUANTITY"]
                ]
                
                if numbers:
                    market_size = {
                        'value': numbers[0],
                        'context': sent.text,
                        'year': self._extract_year(sent),
                        'source': doc.user_data.get('source_url', ''),
                        'confidence': self._calculate_confidence(sent)
                    }
                    market_sizes.append(market_size)
        
        return market_sizes

    def _extract_year(self, sent) -> Optional[str]:
        """Extract year from sentence."""
        # Look for years in text
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, sent.text)
        
        if years:
            return years[0]
        return None

    def _calculate_confidence(self, sent) -> float:
        """Calculate confidence score for extracted information."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for specific indicators
        confidence_indicators = [
            "estimated", "reported", "according to",
            "research shows", "data indicates"
        ]
        
        # Decrease confidence for uncertain language
        uncertainty_indicators = [
            "approximately", "around", "about",
            "roughly", "estimated", "projected"
        ]
        
        sent_text = sent.text.lower()
        
        # Adjust confidence based on indicators
        for indicator in confidence_indicators:
            if indicator in sent_text:
                confidence += 0.1
            
        for indicator in uncertainty_indicators:
            if indicator in sent_text:
                confidence -= 0.1
        
        # Ensure confidence stays between 0 and 1
        return max(0.0, min(1.0, confidence))

    def _extract_growth_rates(self, doc) -> List[Dict[str, Any]]:
        """Extract growth rate information from text."""
        growth_rates = []
        
        # Look for growth rate indicators
        growth_indicators = [
            "growth rate", "CAGR", "year-over-year",
            "YoY", "increase", "growth projection",
            "annual growth", "compound growth"
        ]
        
        # Look for percentage patterns
        percentage_pattern = r'(\d+\.?\d*)%'
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Check if sentence contains growth indicators
            if any(indicator in sent_text for indicator in growth_indicators):
                # Extract percentages
                percentages = re.findall(percentage_pattern, sent.text)
                
                # Extract time periods
                time_period = self._extract_time_period(sent)
                
                if percentages:
                    growth_rate = {
                        'rate': float(percentages[0]),
                        'context': sent.text,
                        'time_period': time_period,
                        'source': doc.user_data.get('source_url', ''),
                        'confidence': self._calculate_confidence(sent),
                        'type': self._determine_growth_type(sent)
                    }
                    growth_rates.append(growth_rate)
        
        return growth_rates

    def _extract_time_period(self, sent) -> Optional[str]:
        """Extract time period information from sentence."""
        time_indicators = {
            'annual': 'yearly',
            'yearly': 'yearly',
            'monthly': 'monthly',
            'quarterly': 'quarterly',
            'year-over-year': 'yearly',
            'yoy': 'yearly',
            'per year': 'yearly',
            'per month': 'monthly',
            'per quarter': 'quarterly'
        }
        
        sent_text = sent.text.lower()
        
        for indicator, period in time_indicators.items():
            if indicator in sent_text:
                return period
            
        return None

    def _determine_growth_type(self, sent) -> str:
        """Determine type of growth mentioned."""
        type_indicators = {
            'revenue': ['revenue', 'sales', 'income'],
            'user': ['user', 'customer', 'client', 'subscriber'],
            'market': ['market', 'industry', 'sector'],
            'adoption': ['adoption', 'usage', 'penetration'],
            'engagement': ['engagement', 'activity', 'interaction']
        }
        
        sent_text = sent.text.lower()
        
        for growth_type, indicators in type_indicators.items():
            if any(indicator in sent_text for indicator in indicators):
                return growth_type
            
        return 'general'

    def _calculate_theme_relevance(self, theme: str, content: str) -> float:
        """Calculate relevance score for a theme."""
        try:
            relevance = 0.0
            content_lower = content.lower()
            theme_lower = theme.lower()
            
            # Base frequency score (0-0.4)
            theme_count = content_lower.count(theme_lower)
            max_expected_count = 10  # Adjust based on typical content length
            frequency_score = min(0.4, (theme_count / max_expected_count) * 0.4)
            relevance += frequency_score
            
            # Context score (0-0.3)
            context_indicators = [
                "important", "key", "significant", "essential",
                "primary", "major", "critical", "core",
                "focus", "main", "central", "crucial"
            ]
            
            # Find sentences containing the theme
            doc = self.nlp(content)
            theme_sentences = [
                sent.text.lower() 
                for sent in doc.sents 
                if theme_lower in sent.text.lower()
            ]
            
            # Calculate context score
            context_score = 0.0
            for sentence in theme_sentences:
                if any(indicator in sentence for indicator in context_indicators):
                    context_score += 0.1
            context_score = min(0.3, context_score)
            relevance += context_score
            
            # Position score (0-0.3)
            # Themes appearing earlier in the content are considered more relevant
            first_occurrence = content_lower.find(theme_lower)
            if first_occurrence != -1:
                relative_position = first_occurrence / len(content)
                position_score = 0.3 * (1 - min(1.0, relative_position / 0.5))
                relevance += position_score
            
            # Ensure final score is between 0 and 1
            return min(1.0, relevance)
            
        except Exception as e:
            logger.error(f"Error calculating theme relevance: {str(e)}")
            return 0.0

    def _merge_related_themes(self, themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge related themes to avoid redundancy."""
        try:
            merged = []
            processed = set()
            
            for theme in themes:
                if theme['name'] in processed:
                    continue
                    
                # Find related themes
                related = [
                    t for t in themes 
                    if self._are_themes_related(theme['name'], t['name'])
                    and t['name'] not in processed
                ]
                
                if related:
                    # Merge related themes
                    merged_theme = {
                        'name': theme['name'],  # Use primary theme name
                        'frequency': sum(t['frequency'] for t in related),
                        'sentiment': sum(t['sentiment'] for t in related) / len(related),
                        'source_url': theme['source_url'],
                        'related_entities': list(set(
                            entity 
                            for t in related 
                            for entity in t['related_entities']
                        )),
                        'relevance': max(t['relevance'] for t in related)
                    }
                    merged.append(merged_theme)
                    
                    # Mark all related themes as processed
                    processed.update(t['name'] for t in related)
                else:
                    merged.append(theme)
                    processed.add(theme['name'])
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging themes: {str(e)}")
            return themes

    def _are_themes_related(self, theme1: str, theme2: str) -> bool:
        """Determine if two themes are related."""
        try:
            # If themes are identical or one contains the other
            if theme1 == theme2 or theme1 in theme2 or theme2 in theme1:
                return True
            
            # Calculate similarity using spaCy
            try:
                doc1 = self.nlp(theme1)
                doc2 = self.nlp(theme2)
                if not doc1.vector_norm or not doc2.vector_norm:
                    # Fall back to string matching if vectors aren't available
                    return (
                        len(set(theme1.lower().split()) & set(theme2.lower().split())) > 0
                    )
                similarity = doc1.similarity(doc2)
                return similarity > 0.8
            except Exception as e:
                logger.warning(f"Error calculating similarity: {str(e)}")
                # Fall back to basic string matching
                return (
                    len(set(theme1.lower().split()) & set(theme2.lower().split())) > 0
                )
            
        except Exception as e:
            logger.error(f"Error comparing themes: {str(e)}")
            return False

    def _analyze_market_trends(self, research_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze market trends from research."""
        logger.info("Analyzing market trends...")
        trends = []
        for result in research_results:
            doc = self.nlp(result['content'])
            trend_data = self._extract_trends(doc)
            if trend_data:
                trends.extend(trend_data)
        return trends

    def _analyze_competition(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive landscape."""
        logger.info("Analyzing competitive landscape...")
        competitors = []
        for result in research_results:
            doc = self.nlp(result['content'])
            competitor_data = self._extract_competitors(doc)
            if competitor_data:
                competitors.extend(competitor_data)
        return {
            'competitors': competitors,
            'total_competitors': len(competitors),
            'market_leaders': [c for c in competitors if 'leader' in c['mention_context'].lower()]
        }

    def _identify_opportunities(self, research_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify key opportunities from research."""
        logger.info("Identifying market opportunities...")
        opportunities = []
        opportunity_indicators = [
            "opportunity", "potential", "growth",
            "emerging", "untapped", "promising"
        ]
        
        for result in research_results:
            doc = self.nlp(result['content'])
            for sent in doc.sents:
                if any(indicator in sent.text.lower() for indicator in opportunity_indicators):
                    opportunities.append({
                        'description': sent.text,
                        'source': result['url'],
                        'confidence': self._calculate_confidence(sent)
                    })
        return opportunities

    async def get_progress_state(self) -> Dict[str, Any]:
        """Get current progress state."""
        if self.web_tracker:
            return await self.web_tracker.update(
                self.current_stage or "",
                self.overall_progress,
                self.completed_steps
            )
        return {
            'status': self.current_stage or "",
            'progress': self.overall_progress,
            'completed_steps': self.completed_steps
        }