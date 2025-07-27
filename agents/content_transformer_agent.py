"""
Content Transformer Agent - Responsible for transforming Instagram content for different platforms
"""
import asyncio
from typing import Dict, List, Optional
from crewai import Agent, Task
from loguru import logger
from services.content_analyzer import ContentAnalyzer
from utils.text_generator import TextGenerator
from config import settings, CONTENT_PROMPTS, PLATFORM_CONFIGS

class ContentTransformerAgent:
    """Agent responsible for transforming content for different social media platforms"""
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.text_generator = TextGenerator()
        
        # Define the CrewAI agent
        self.agent = Agent(
            role="Content Transformation Specialist",
            goal="Transform Instagram video content into platform-optimized posts for Twitter and LinkedIn",
            backstory="""You are an expert content strategist who understands the nuances 
            of different social media platforms. You know how to adapt content to match 
            platform-specific audiences, tone, and format requirements while maintaining 
            the core message and engagement potential.""",
            verbose=True,
            allow_delegation=False
        )
    
    async def transform_content(self, video_data: Dict, target_platforms: List[str]) -> Dict:
        """
        Transform video content for specified platforms
        
        Args:
            video_data: Processed Instagram video data
            target_platforms: List of platforms to transform for ('twitter', 'linkedin')
            
        Returns:
            Dictionary with transformed content for each platform
        """
        try:
            logger.info(f"Transforming content {video_data['id']} for platforms: {target_platforms}")
            
            # Analyze video content
            content_analysis = await self.content_analyzer.analyze_video_content(
                video_data['video_path'],
                video_data['caption']
            )
            
            transformed_content = {}
            
            for platform in target_platforms:
                if platform in PLATFORM_CONFIGS:
                    platform_content = await self._transform_for_platform(
                        video_data, content_analysis, platform
                    )
                    transformed_content[platform] = platform_content
            
            return transformed_content
            
        except Exception as e:
            logger.error(f"Error transforming content {video_data.get('id', 'unknown')}: {str(e)}")
            return {}
    
    async def _transform_for_platform(self, video_data: Dict, analysis: Dict, platform: str) -> Dict:
        """
        Transform content for a specific platform
        
        Args:
            video_data: Original video data
            analysis: Content analysis results
            platform: Target platform ('twitter' or 'linkedin')
            
        Returns:
            Platform-specific content dictionary
        """
        try:
            platform_config = PLATFORM_CONFIGS[platform]
            
            # Generate platform-specific text
            prompt = CONTENT_PROMPTS[platform].format(
                content=video_data['caption'],
                description=analysis.get('description', '')
            )
            
            generated_text = await self.text_generator.generate_text(
                prompt,
                max_length=platform_config['max_length']
            )
            
            # Extract hashtags and mentions
            hashtags = self._extract_hashtags(
                generated_text, 
                video_data.get('hashtags', []),
                platform_config['hashtag_limit']
            )
            
            # Prepare media
            media_info = await self._prepare_media_for_platform(
                video_data, platform_config
            )
            
            platform_content = {
                'text': generated_text,
                'hashtags': hashtags,
                'media': media_info,
                'original_id': video_data['id'],
                'platform': platform,
                'engagement_score': analysis.get('engagement_score', 0),
                'topics': analysis.get('topics', []),
                'sentiment': analysis.get('sentiment', 'neutral')
            }
            
            return platform_content
            
        except Exception as e:
            logger.error(f"Error transforming for {platform}: {str(e)}")
            return {}
    
    def _extract_hashtags(self, text: str, original_hashtags: List[str], limit: int) -> List[str]:
        """
        Extract and optimize hashtags for the platform
        
        Args:
            text: Generated text content
            original_hashtags: Original Instagram hashtags
            limit: Maximum number of hashtags for the platform
            
        Returns:
            List of optimized hashtags
        """
        # Extract hashtags from generated text
        import re
        text_hashtags = re.findall(r'#\w+', text)
        
        # Combine with original hashtags
        all_hashtags = list(set(text_hashtags + [f"#{tag}" for tag in original_hashtags if not tag.startswith('#')]))
        
        # Limit to platform maximum
        return all_hashtags[:limit]
    
    async def _prepare_media_for_platform(self, video_data: Dict, platform_config: Dict) -> Dict:
        """
        Prepare media content for the platform
        
        Args:
            video_data: Original video data
            platform_config: Platform-specific configuration
            
        Returns:
            Media information dictionary
        """
        try:
            video_info = video_data.get('video_info', {})
            
            # Check if video meets platform requirements
            duration = video_info.get('duration', 0)
            file_size = video_info.get('file_size', 0)
            
            if (duration <= platform_config['video_max_duration'] and 
                file_size <= platform_config['video_max_size']):
                
                return {
                    'type': 'video',
                    'path': video_data['video_path'],
                    'duration': duration,
                    'size': file_size,
                    'thumbnail': video_data.get('thumbnail_url')
                }
            else:
                # Use thumbnail if video doesn't meet requirements
                return {
                    'type': 'image',
                    'path': video_data.get('thumbnail_url'),
                    'note': 'Video too large/long for platform, using thumbnail'
                }
                
        except Exception as e:
            logger.error(f"Error preparing media: {str(e)}")
            return {}
    
    def create_transformation_task(self, video_data_list: List[Dict], platforms: List[str]) -> Task:
        """
        Create a CrewAI task for content transformation
        
        Args:
            video_data_list: List of video data to transform
            platforms: Target platforms for transformation
            
        Returns:
            CrewAI Task object
        """
        return Task(
            description=f"""
            Transform {len(video_data_list)} Instagram videos into optimized content for {', '.join(platforms)}.
            
            For each video:
            1. Analyze the video content and context
            2. Generate platform-specific text that maintains engagement
            3. Optimize hashtags for each platform
            4. Prepare media content according to platform requirements
            5. Ensure content follows platform best practices
            
            Platforms: {platforms}
            Focus on maintaining the original message while optimizing for each platform's audience.
            """,
            agent=self.agent,
            expected_output="Dictionary of transformed content for each platform and video"
        )
    
    async def execute_transformation(self, video_data_list: List[Dict], platforms: List[str]) -> List[Dict]:
        """
        Execute content transformation for multiple videos
        
        Args:
            video_data_list: List of video data to transform
            platforms: Target platforms
            
        Returns:
            List of transformed content for all videos and platforms
        """
        transformed_results = []
        
        for video_data in video_data_list:
            transformed_content = await self.transform_content(video_data, platforms)
            if transformed_content:
                transformed_results.append({
                    'original_video': video_data,
                    'transformed_content': transformed_content
                })
        
        logger.info(f"Successfully transformed {len(transformed_results)} videos for {len(platforms)} platforms")
        return transformed_results
