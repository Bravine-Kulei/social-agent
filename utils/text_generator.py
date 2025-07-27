"""
Text Generation Utilities using AI models
"""
import asyncio
from typing import Dict, List, Optional
import openai
from anthropic import Anthropic
from loguru import logger
from config import settings

class TextGenerator:
    """Utility class for AI-powered text generation"""
    
    def __init__(self):
        # Initialize OpenAI
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_available = True
        else:
            self.openai_available = False
            logger.warning("OpenAI API key not provided")
        
        # Initialize Anthropic
        if settings.anthropic_api_key:
            self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
            self.anthropic_available = True
        else:
            self.anthropic_available = False
            logger.warning("Anthropic API key not provided")
    
    async def generate_text(self, prompt: str, max_length: int = 280, model: str = "openai") -> str:
        """
        Generate text using AI models
        
        Args:
            prompt: Input prompt for text generation
            max_length: Maximum length of generated text
            model: Model to use ("openai" or "anthropic")
            
        Returns:
            Generated text
        """
        try:
            if model == "openai" and self.openai_available:
                return await self._generate_with_openai(prompt, max_length)
            elif model == "anthropic" and self.anthropic_available:
                return await self._generate_with_anthropic(prompt, max_length)
            else:
                logger.warning(f"Model {model} not available, using fallback")
                return await self._generate_fallback(prompt, max_length)
                
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return await self._generate_fallback(prompt, max_length)
    
    async def _generate_with_openai(self, prompt: str, max_length: int) -> str:
        """Generate text using OpenAI GPT"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a social media content creator. Generate engaging content that is exactly under {max_length} characters."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_length // 2,  # Rough estimate for token to character ratio
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            # Ensure text is within length limit
            if len(generated_text) > max_length:
                generated_text = generated_text[:max_length-3] + "..."
            
            return generated_text
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            raise
    
    async def _generate_with_anthropic(self, prompt: str, max_length: int) -> str:
        """Generate text using Anthropic Claude"""
        try:
            message = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_length // 2,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate social media content (max {max_length} characters): {prompt}"
                    }
                ]
            )
            
            generated_text = message.content[0].text.strip()
            
            # Ensure text is within length limit
            if len(generated_text) > max_length:
                generated_text = generated_text[:max_length-3] + "..."
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {str(e)}")
            raise
    
    async def _generate_fallback(self, prompt: str, max_length: int) -> str:
        """Fallback text generation when AI models are unavailable"""
        # Simple template-based generation as fallback
        templates = [
            "Check out this amazing content! 🔥",
            "Don't miss this incredible video! ✨",
            "This is absolutely mind-blowing! 🤯",
            "You have to see this! 👀",
            "This content is pure gold! ⭐"
        ]
        
        import random
        base_text = random.choice(templates)
        
        # Add hashtags if space allows
        hashtags = ["#viral", "#amazing", "#content", "#video", "#social"]
        for hashtag in hashtags:
            if len(base_text) + len(hashtag) + 1 <= max_length:
                base_text += f" {hashtag}"
            else:
                break
        
        return base_text
    
    async def generate_hashtags(self, content: str, platform: str, max_hashtags: int = 10) -> List[str]:
        """
        Generate relevant hashtags for content
        
        Args:
            content: Content to generate hashtags for
            platform: Target platform ("twitter" or "linkedin")
            max_hashtags: Maximum number of hashtags to generate
            
        Returns:
            List of hashtags
        """
        try:
            prompt = f"""
            Generate {max_hashtags} relevant hashtags for this {platform} content:
            
            Content: {content}
            
            Requirements:
            - Hashtags should be relevant and trending
            - Mix of broad and specific hashtags
            - Appropriate for {platform} audience
            - Return only hashtags, one per line, with # symbol
            """
            
            generated_text = await self.generate_text(prompt, max_length=500)
            
            # Extract hashtags from generated text
            hashtags = []
            for line in generated_text.split('\n'):
                line = line.strip()
                if line.startswith('#') and len(hashtags) < max_hashtags:
                    hashtags.append(line)
            
            return hashtags[:max_hashtags]
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return self._get_default_hashtags(platform)
    
    def _get_default_hashtags(self, platform: str) -> List[str]:
        """Get default hashtags for platform"""
        if platform == "twitter":
            return ["#viral", "#content", "#video", "#social", "#trending"]
        elif platform == "linkedin":
            return ["#professional", "#business", "#content", "#networking", "#industry"]
        else:
            return ["#content", "#video", "#social"]
    
    async def optimize_for_platform(self, text: str, platform: str) -> str:
        """
        Optimize text content for specific platform
        
        Args:
            text: Original text
            platform: Target platform
            
        Returns:
            Platform-optimized text
        """
        try:
            if platform == "twitter":
                max_length = 280
                tone = "casual and engaging"
            elif platform == "linkedin":
                max_length = 3000
                tone = "professional and insightful"
            else:
                max_length = 500
                tone = "engaging"
            
            prompt = f"""
            Optimize this content for {platform}:
            
            Original: {text}
            
            Requirements:
            - {tone} tone
            - Maximum {max_length} characters
            - Platform-appropriate language and style
            - Maintain core message
            """
            
            optimized_text = await self.generate_text(prompt, max_length)
            return optimized_text
            
        except Exception as e:
            logger.error(f"Error optimizing for {platform}: {str(e)}")
            return text[:280] if platform == "twitter" else text
    
    async def generate_call_to_action(self, content_type: str, platform: str) -> str:
        """
        Generate call-to-action text
        
        Args:
            content_type: Type of content (video, image, etc.)
            platform: Target platform
            
        Returns:
            Call-to-action text
        """
        try:
            cta_templates = {
                "twitter": [
                    "What do you think? 💭",
                    "Share your thoughts! 👇",
                    "RT if you agree! 🔄",
                    "Tag someone who needs to see this! 👥",
                    "Drop a ❤️ if you love this!"
                ],
                "linkedin": [
                    "What's your take on this?",
                    "Share your professional insights below.",
                    "How does this relate to your industry experience?",
                    "Connect with me to discuss further.",
                    "What strategies have worked for you?"
                ]
            }
            
            import random
            ctas = cta_templates.get(platform, cta_templates["twitter"])
            return random.choice(ctas)
            
        except Exception as e:
            logger.error(f"Error generating CTA: {str(e)}")
            return "What do you think?"
    
    async def summarize_content(self, content: str, max_length: int = 100) -> str:
        """
        Generate a summary of content
        
        Args:
            content: Content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Content summary
        """
        try:
            prompt = f"""
            Summarize this content in {max_length} characters or less:
            
            {content}
            
            Make it engaging and capture the key points.
            """
            
            summary = await self.generate_text(prompt, max_length)
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing content: {str(e)}")
            return content[:max_length] + "..." if len(content) > max_length else content
    
    async def generate_thread(self, content: str, max_tweets: int = 5) -> List[str]:
        """
        Generate a Twitter thread from content
        
        Args:
            content: Content to convert to thread
            max_tweets: Maximum number of tweets in thread
            
        Returns:
            List of tweet texts
        """
        try:
            prompt = f"""
            Convert this content into a Twitter thread of {max_tweets} tweets maximum:
            
            {content}
            
            Requirements:
            - Each tweet must be under 280 characters
            - Maintain narrative flow
            - Use thread numbering (1/n, 2/n, etc.)
            - Engaging and informative
            """
            
            thread_text = await self.generate_text(prompt, max_length=1400)  # 5 tweets * 280 chars
            
            # Split into individual tweets
            tweets = []
            for line in thread_text.split('\n'):
                line = line.strip()
                if line and len(line) <= 280:
                    tweets.append(line)
                    if len(tweets) >= max_tweets:
                        break
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error generating thread: {str(e)}")
            return [content[:280]]
