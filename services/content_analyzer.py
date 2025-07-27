"""
Content Analyzer Service - Analyzes video content and generates insights
"""
import asyncio
import cv2
import os
from typing import Dict, List, Optional, Tuple
import openai
from transformers import pipeline
from loguru import logger
from config import settings

class ContentAnalyzer:
    """Service for analyzing video content and generating insights"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = settings.openai_api_key
        
        # Initialize sentiment analysis pipeline
        try:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        except Exception as e:
            logger.warning(f"Failed to load sentiment analyzer: {str(e)}")
            self.sentiment_analyzer = None
        
        # Initialize topic classification pipeline
        try:
            self.topic_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except Exception as e:
            logger.warning(f"Failed to load topic classifier: {str(e)}")
            self.topic_classifier = None
    
    async def analyze_video_content(self, video_path: str, caption: str = "") -> Dict:
        """
        Comprehensive analysis of video content
        
        Args:
            video_path: Path to the video file
            caption: Video caption text
            
        Returns:
            Analysis results dictionary
        """
        try:
            logger.info(f"Analyzing video content: {os.path.basename(video_path)}")
            
            analysis_results = {
                'video_path': video_path,
                'caption': caption,
                'visual_analysis': {},
                'text_analysis': {},
                'content_summary': {},
                'engagement_score': 0,
                'topics': [],
                'sentiment': 'neutral',
                'description': ''
            }
            
            # Analyze video visually
            visual_analysis = await self._analyze_video_visual(video_path)
            analysis_results['visual_analysis'] = visual_analysis
            
            # Analyze caption text
            if caption:
                text_analysis = await self._analyze_text_content(caption)
                analysis_results['text_analysis'] = text_analysis
                analysis_results['sentiment'] = text_analysis.get('sentiment', 'neutral')
                analysis_results['topics'] = text_analysis.get('topics', [])
            
            # Generate content description using AI
            description = await self._generate_content_description(visual_analysis, caption)
            analysis_results['description'] = description
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(analysis_results)
            analysis_results['engagement_score'] = engagement_score
            
            # Generate content summary
            summary = await self._generate_content_summary(analysis_results)
            analysis_results['content_summary'] = summary
            
            logger.info(f"Video analysis completed: {os.path.basename(video_path)}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing video content: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_video_visual(self, video_path: str) -> Dict:
        """
        Analyze visual aspects of the video
        
        Args:
            video_path: Path to video file
            
        Returns:
            Visual analysis results
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Sample frames for analysis
            sample_frames = []
            frame_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    sample_frames.append(frame)
            
            cap.release()
            
            # Analyze frames
            visual_features = {
                'duration': duration,
                'fps': fps,
                'resolution': f"{width}x{height}",
                'frame_count': frame_count,
                'aspect_ratio': width / height if height > 0 else 1,
                'brightness_avg': self._calculate_brightness(sample_frames),
                'color_dominance': self._analyze_color_dominance(sample_frames),
                'motion_level': self._estimate_motion_level(sample_frames),
                'scene_changes': len(sample_frames)  # Simplified scene change detection
            }
            
            return visual_features
            
        except Exception as e:
            logger.error(f"Error in visual analysis: {str(e)}")
            return {}
    
    def _calculate_brightness(self, frames: List) -> float:
        """Calculate average brightness of frames"""
        if not frames:
            return 0
        
        brightness_values = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = gray.mean()
            brightness_values.append(brightness)
        
        return sum(brightness_values) / len(brightness_values)
    
    def _analyze_color_dominance(self, frames: List) -> Dict:
        """Analyze dominant colors in frames"""
        if not frames:
            return {}
        
        # Simplified color analysis
        color_channels = {'blue': [], 'green': [], 'red': []}
        
        for frame in frames:
            b, g, r = cv2.split(frame)
            color_channels['blue'].append(b.mean())
            color_channels['green'].append(g.mean())
            color_channels['red'].append(r.mean())
        
        dominant_colors = {
            color: sum(values) / len(values) 
            for color, values in color_channels.items()
        }
        
        return dominant_colors
    
    def _estimate_motion_level(self, frames: List) -> str:
        """Estimate motion level in video"""
        if len(frames) < 2:
            return "static"
        
        # Calculate frame differences
        motion_scores = []
        for i in range(1, len(frames)):
            diff = cv2.absdiff(frames[i-1], frames[i])
            motion_score = diff.mean()
            motion_scores.append(motion_score)
        
        avg_motion = sum(motion_scores) / len(motion_scores)
        
        if avg_motion < 10:
            return "low"
        elif avg_motion < 30:
            return "medium"
        else:
            return "high"
    
    async def _analyze_text_content(self, text: str) -> Dict:
        """
        Analyze text content for sentiment and topics
        
        Args:
            text: Text to analyze
            
        Returns:
            Text analysis results
        """
        try:
            analysis = {}
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                sentiment_result = self.sentiment_analyzer(text)
                analysis['sentiment'] = sentiment_result[0]['label'].lower()
                analysis['sentiment_score'] = sentiment_result[0]['score']
            
            # Topic classification
            if self.topic_classifier:
                candidate_labels = [
                    "entertainment", "education", "lifestyle", "technology", 
                    "business", "sports", "travel", "food", "fashion", 
                    "music", "art", "fitness", "comedy", "news"
                ]
                topic_result = self.topic_classifier(text, candidate_labels)
                analysis['topics'] = topic_result['labels'][:3]  # Top 3 topics
                analysis['topic_scores'] = topic_result['scores'][:3]
            
            # Text statistics
            analysis['word_count'] = len(text.split())
            analysis['character_count'] = len(text)
            analysis['hashtag_count'] = text.count('#')
            analysis['mention_count'] = text.count('@')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            return {}
    
    async def _generate_content_description(self, visual_analysis: Dict, caption: str) -> str:
        """
        Generate AI description of content
        
        Args:
            visual_analysis: Visual analysis results
            caption: Original caption
            
        Returns:
            Generated description
        """
        try:
            prompt = f"""
            Analyze this video content and provide a concise description:
            
            Visual Analysis:
            - Duration: {visual_analysis.get('duration', 0):.1f} seconds
            - Motion Level: {visual_analysis.get('motion_level', 'unknown')}
            - Brightness: {visual_analysis.get('brightness_avg', 0):.1f}
            - Resolution: {visual_analysis.get('resolution', 'unknown')}
            
            Caption: {caption}
            
            Provide a 2-3 sentence description of what this video likely contains and its potential appeal.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating description: {str(e)}")
            return "Video content analysis description unavailable."
    
    def _calculate_engagement_score(self, analysis: Dict) -> float:
        """
        Calculate predicted engagement score based on analysis
        
        Args:
            analysis: Complete analysis results
            
        Returns:
            Engagement score (0-100)
        """
        try:
            score = 50  # Base score
            
            # Visual factors
            visual = analysis.get('visual_analysis', {})
            duration = visual.get('duration', 0)
            
            # Optimal duration bonus (15-60 seconds)
            if 15 <= duration <= 60:
                score += 15
            elif duration < 15:
                score += 5
            
            # Motion level bonus
            motion = visual.get('motion_level', 'low')
            if motion == 'medium':
                score += 10
            elif motion == 'high':
                score += 5
            
            # Text factors
            text = analysis.get('text_analysis', {})
            
            # Sentiment bonus
            sentiment = text.get('sentiment', 'neutral')
            if sentiment == 'positive':
                score += 15
            elif sentiment == 'negative':
                score -= 5
            
            # Hashtag bonus (optimal 3-7 hashtags)
            hashtag_count = text.get('hashtag_count', 0)
            if 3 <= hashtag_count <= 7:
                score += 10
            elif hashtag_count > 10:
                score -= 5
            
            # Word count bonus (optimal 20-100 words)
            word_count = text.get('word_count', 0)
            if 20 <= word_count <= 100:
                score += 10
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 50
    
    async def _generate_content_summary(self, analysis: Dict) -> Dict:
        """Generate a summary of the content analysis"""
        try:
            visual = analysis.get('visual_analysis', {})
            text = analysis.get('text_analysis', {})
            
            summary = {
                'content_type': 'video',
                'duration_category': self._categorize_duration(visual.get('duration', 0)),
                'motion_level': visual.get('motion_level', 'unknown'),
                'primary_topic': text.get('topics', ['general'])[0] if text.get('topics') else 'general',
                'sentiment': analysis.get('sentiment', 'neutral'),
                'engagement_potential': self._categorize_engagement(analysis.get('engagement_score', 50)),
                'recommended_platforms': self._recommend_platforms(analysis)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {}
    
    def _categorize_duration(self, duration: float) -> str:
        """Categorize video duration"""
        if duration < 15:
            return "short"
        elif duration < 60:
            return "medium"
        else:
            return "long"
    
    def _categorize_engagement(self, score: float) -> str:
        """Categorize engagement potential"""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"
    
    def _recommend_platforms(self, analysis: Dict) -> List[str]:
        """Recommend best platforms based on analysis"""
        recommendations = []
        
        visual = analysis.get('visual_analysis', {})
        text = analysis.get('text_analysis', {})
        
        duration = visual.get('duration', 0)
        topics = text.get('topics', [])
        
        # Twitter recommendations
        if duration <= 140 and any(topic in ['news', 'entertainment', 'comedy'] for topic in topics):
            recommendations.append('twitter')
        
        # LinkedIn recommendations
        if any(topic in ['business', 'technology', 'education'] for topic in topics):
            recommendations.append('linkedin')
        
        # Default to both if no specific recommendations
        if not recommendations:
            recommendations = ['twitter', 'linkedin']
        
        return recommendations
