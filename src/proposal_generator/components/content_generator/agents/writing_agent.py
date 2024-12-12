"""Writing agent for content generation."""
from typing import Dict, Any, List, Optional
import logging
from ..models.content_model import (
    ContentRequest,
    ContentType,
    ContentTone,
    ContentSection,
    GeneratedContent,
    ContentMetrics
)

logger = logging.getLogger(__name__)

class WritingAgent:
    """Agent responsible for generating content."""
    
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def generate_content(self, request: ContentRequest, 
                        topic_analysis: Dict[str, Any]) -> GeneratedContent:
        """
        Generate content based on request and topic analysis.
        
        Args:
            request: Content generation request
            topic_analysis: Analysis from topic analyzer
            
        Returns:
            Generated content
        """
        try:
            if self.progress_callback:
                self.progress_callback("Starting content generation...", 0)
            
            # Generate sections
            sections = []
            total_sections = len(topic_analysis['outline']['sections'])
            
            for i, section_outline in enumerate(topic_analysis['outline']['sections']):
                if self.progress_callback:
                    progress = int((i / total_sections) * 80)  # 0-80%
                    self.progress_callback(f"Generating section: {section_outline['name']}", progress)
                
                section = self._generate_section(
                    section_outline,
                    request,
                    topic_analysis['themes_by_section'].get(section_outline['name'], [])
                )
                sections.append(section)

            if self.progress_callback:
                self.progress_callback("Calculating metrics...", 80)
            
            # Combine sections into full content
            full_content = "\n\n".join([
                f"# {section.title}\n{section.content}"
                for section in sections
            ])

            return GeneratedContent(
                content_type=request.content_type,
                title=self._generate_title(request, sections),
                content=full_content,
                sections=sections,
                metadata={
                    'target_audience': request.target_audience,
                    'tone': request.tone.value,
                    'analysis': topic_analysis['metadata']
                },
                metrics=self._calculate_content_metrics(sections),
                summary=self._generate_summary(sections),
                recommendations=self._generate_recommendations(sections)
            )

        except Exception as e:
            if self.progress_callback:
                self.progress_callback(f"Error generating content: {str(e)}", 0)
            return self._create_empty_content(request)

    def _generate_section(self, outline: Dict[str, Any], request: ContentRequest,
                         themes: List[str]) -> ContentSection:
        """Generate content for a section."""
        try:
            # Generate main content
            content = self._generate_section_content(
                outline['name'],
                outline['expected_content'],
                outline['key_points'],
                themes,
                request
            )

            # Extract keywords
            keywords = self._extract_keywords(content, themes)

            # Calculate section metrics
            metrics = self._calculate_section_metrics(content, keywords)

            # Gather references
            references = self._gather_references(content, request.reference_data)

            return ContentSection(
                title=outline['name'],
                content=content,
                keywords=keywords,
                metrics=metrics,
                references=references
            )

        except Exception as e:
            logger.error(f"Error generating section {outline['name']}: {str(e)}")
            return self._create_empty_section(outline['name'])

    def _generate_section_content(self, name: str, expected_content: str,
                                key_points: List[str], themes: List[str],
                                request: ContentRequest) -> str:
        """Generate the actual content for a section."""
        try:
            content_parts = []

            # Add introduction
            intro = self._generate_introduction(name, expected_content, request.tone)
            content_parts.append(intro)

            # Add main points
            for point in key_points:
                point_content = self._generate_point_content(
                    point,
                    themes,
                    request.tone,
                    request.target_audience
                )
                content_parts.append(point_content)

            # Add supporting details
            if themes:
                details = self._generate_supporting_details(themes, request.tone)
                content_parts.append(details)

            # Add conclusion
            conclusion = self._generate_conclusion(name, key_points, request.tone)
            content_parts.append(conclusion)

            return "\n\n".join(content_parts)

        except Exception as e:
            logger.error(f"Error generating section content: {str(e)}")
            return f"Content for {name}"

    def _calculate_content_metrics(self, sections: List[ContentSection]) -> Dict[str, Any]:
        """Calculate metrics for the entire content."""
        try:
            # Combine all content
            all_content = " ".join(section.content for section in sections)
            all_keywords = set()
            for section in sections:
                all_keywords.update(section.keywords)

            # Calculate base metrics
            metrics = {
                'word_count': len(all_content.split()),
                'readability_score': self._calculate_readability(all_content),
                'keyword_density': self._calculate_keyword_density(all_content, all_keywords),
                'sentiment_score': self._calculate_sentiment(all_content),
                'technical_complexity': self._calculate_technical_complexity(all_content),
                'uniqueness_score': self._calculate_uniqueness(all_content),
                'quality_score': 0.0  # Will be calculated below
            }

            # Calculate overall quality score
            metrics['quality_score'] = self._calculate_quality_score(metrics)

            return metrics

        except Exception as e:
            logger.error(f"Error calculating content metrics: {str(e)}")
            return {
                'word_count': 0,
                'readability_score': 0.0,
                'keyword_density': {},
                'sentiment_score': 0.0,
                'technical_complexity': 0.0,
                'uniqueness_score': 0.0,
                'quality_score': 0.0
            }

    def _generate_summary(self, sections: List[ContentSection],
                         metrics: Dict[str, Any]) -> str:
        """Generate content summary."""
        try:
            summary_parts = []

            # Add overview
            summary_parts.append("Executive Summary:")

            # Add key points from each section
            for section in sections:
                key_points = self._extract_key_points(section.content)
                if key_points:
                    summary_parts.append(f"\n{section.title}:")
                    summary_parts.extend([f"- {point}" for point in key_points[:3]])

            # Add metrics summary
            summary_parts.append("\nContent Overview:")
            summary_parts.append(f"- Total length: {metrics['word_count']} words")
            summary_parts.append(f"- Overall quality score: {metrics['quality_score']:.2f}")

            return "\n".join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary not available"

    def _generate_recommendations(self, sections: List[ContentSection],
                                metrics: Dict[str, Any]) -> List[str]:
        """Generate content recommendations."""
        try:
            recommendations = []

            # Check content length
            if metrics['word_count'] < 1000:
                recommendations.append("Consider expanding content for better depth")
            elif metrics['word_count'] > 5000:
                recommendations.append("Consider condensing content for better focus")

            # Check readability
            if metrics['readability_score'] < 0.6:
                recommendations.append("Improve content readability with simpler language")

            # Check keyword usage
            low_density_keywords = [
                k for k, d in metrics['keyword_density'].items() if d < 0.01
            ]
            if low_density_keywords:
                recommendations.append(
                    "Increase usage of key terms: " + ", ".join(low_density_keywords[:3])
                )

            # Check technical complexity
            if metrics['technical_complexity'] > 0.7:
                recommendations.append(
                    "Consider simplifying technical language for better understanding"
                )

            # Check section balance
            section_lengths = [len(s.content.split()) for s in sections]
            if max(section_lengths) > 3 * min(section_lengths):
                recommendations.append("Balance section lengths for better flow")

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []

    def _create_empty_content(self, request: ContentRequest) -> GeneratedContent:
        """Create empty generated content."""
        return GeneratedContent(
            content_type=request.content_type,
            title="",
            sections=[],
            metadata={},
            metrics={},
            summary="",
            recommendations=[]
        )

    def _create_empty_section(self, name: str) -> ContentSection:
        """Create empty content section."""
        return ContentSection(
            title=name,
            content="",
            keywords=[],
            metrics={},
            references=[]
        )

    def _generate_title(self, request: ContentRequest,
                       sections: List[ContentSection]) -> str:
        """Generate content title."""
        try:
            if request.content_type == ContentType.PROPOSAL:
                return f"Proposal: {request.target_audience} Solution"
            elif request.content_type == ContentType.TECHNICAL_SPEC:
                return f"Technical Specification: {request.target_audience} Implementation"
            elif request.content_type == ContentType.MARKET_ANALYSIS:
                return f"Market Analysis: {request.target_audience} Segment"
            else:
                return f"{request.content_type.value.title()}: {request.target_audience}"
        except Exception:
            return "Untitled Content"

    def _generate_introduction(self, section_name: str, expected_content: str,
                             tone: ContentTone) -> str:
        """Generate section introduction."""
        try:
            if tone == ContentTone.FORMAL:
                return f"This section provides {expected_content.lower()}."
            elif tone == ContentTone.TECHNICAL:
                return f"Technical overview of {section_name.lower()}."
            else:
                return f"Overview of {expected_content.lower()}."
        except Exception:
            return f"Introduction to {section_name}"

    def _generate_point_content(self, point: str, themes: List[str],
                              tone: ContentTone, audience: str) -> str:
        """Generate content for a key point."""
        try:
            if tone == ContentTone.TECHNICAL:
                return f"Technical analysis shows that {point.lower()}."
            elif tone == ContentTone.PERSUASIVE:
                return f"It is evident that {point.lower()}, which benefits {audience}."
            else:
                return f"{point}."
        except Exception:
            return point

    def _generate_supporting_details(self, themes: List[str],
                                   tone: ContentTone) -> str:
        """Generate supporting details."""
        try:
            if tone == ContentTone.TECHNICAL:
                return "Technical details: " + ", ".join(themes)
            elif tone == ContentTone.PERSUASIVE:
                return "Key benefits include: " + ", ".join(themes)
            else:
                return "Additional details: " + ", ".join(themes)
        except Exception:
            return "Supporting details not available"

    def _generate_conclusion(self, section_name: str, key_points: List[str],
                           tone: ContentTone) -> str:
        """Generate section conclusion."""
        try:
            if tone == ContentTone.FORMAL:
                return f"In conclusion, {section_name.lower()} demonstrates {', '.join(key_points[:2])}."
            elif tone == ContentTone.PERSUASIVE:
                return f"As shown, {', '.join(key_points[:2])} make this solution ideal."
            else:
                return f"To summarize: {', '.join(key_points[:2])}."
        except Exception:
            return f"Conclusion of {section_name}"

    def _extract_keywords(self, content: str, themes: List[str]) -> List[str]:
        """Extract keywords from content."""
        try:
            # Start with themes as base keywords
            keywords = set(themes)

            # Add important words from content
            words = content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Only consider words longer than 4 characters
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Add top frequent words
            top_words = sorted(
                word_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            keywords.update(word for word, _ in top_words)

            return list(keywords)

        except Exception:
            return []

    def _calculate_section_metrics(self, content: str,
                                 keywords: List[str]) -> Dict[str, Any]:
        """Calculate metrics for a section."""
        try:
            return {
                'word_count': len(content.split()),
                'keyword_count': sum(
                    content.lower().count(keyword.lower())
                    for keyword in keywords
                ),
                'average_sentence_length': len(content.split()) / max(
                    len(content.split('.')), 1
                )
            }
        except Exception:
            return {}

    def _gather_references(self, content: str,
                         reference_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gather references used in content."""
        try:
            references = []
            if reference_data:
                for ref_key, ref_value in reference_data.items():
                    if isinstance(ref_value, str) and ref_value.lower() in content.lower():
                        references.append({
                            'type': 'reference',
                            'key': ref_key,
                            'value': ref_value
                        })
            return references
        except Exception:
            return []

    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score."""
        try:
            words = len(text.split())
            sentences = len(text.split('.'))
            avg_words_per_sentence = words / max(sentences, 1)
            return max(0.0, min(1.0, 1.0 - (avg_words_per_sentence - 15) / 10))
        except Exception:
            return 0.0

    def _calculate_keyword_density(self, text: str, keywords: set) -> Dict[str, float]:
        """Calculate keyword density."""
        try:
            word_count = len(text.split())
            return {
                keyword: text.lower().count(keyword.lower()) / max(word_count, 1)
                for keyword in keywords
            }
        except Exception:
            return {}

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score."""
        try:
            # Simplified sentiment analysis
            positive_words = {'good', 'great', 'excellent', 'best', 'innovative'}
            negative_words = {'bad', 'poor', 'worst', 'difficult', 'complex'}

            words = text.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)

            total = positive_count + negative_count
            if total == 0:
                return 0.5
            return positive_count / total

        except Exception:
            return 0.5

    def _calculate_technical_complexity(self, text: str) -> float:
        """Calculate technical complexity score."""
        try:
            technical_indicators = {
                'implementation', 'system', 'architecture', 'database',
                'algorithm', 'framework', 'infrastructure', 'protocol'
            }
            words = text.lower().split()
            technical_count = sum(1 for word in words if word in technical_indicators)
            return min(1.0, technical_count / max(len(words) / 20, 1))
        except Exception:
            return 0.0

    def _calculate_uniqueness(self, text: str) -> float:
        """Calculate uniqueness score."""
        try:
            # Simplified uniqueness calculation
            words = text.lower().split()
            unique_words = len(set(words))
            return unique_words / max(len(words), 1)
        except Exception:
            return 0.0

    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        try:
            weights = {
                'readability_score': 0.3,
                'technical_complexity': 0.2,
                'uniqueness_score': 0.2,
                'sentiment_score': 0.3
            }

            score = sum(
                metrics[metric] * weight
                for metric, weight in weights.items()
                if metric in metrics
            )

            return max(0.0, min(1.0, score))

        except Exception:
            return 0.0

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text."""
        try:
            sentences = text.split('.')
            # Consider sentences that start with key phrases
            key_phrases = ['this shows', 'importantly', 'notably', 'key',
                         'significant', 'essential', 'critical']
            key_points = []

            for sentence in sentences:
                sentence = sentence.strip().lower()
                if any(sentence.startswith(phrase) for phrase in key_phrases):
                    key_points.append(sentence.capitalize())

            return key_points[:3]  # Return top 3 key points

        except Exception:
            return [] 