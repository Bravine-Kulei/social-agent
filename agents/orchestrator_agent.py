"""
Orchestrator Agent - Main coordination agent for the Instagram-to-Social Media system
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew
from loguru import logger

from .instagram_agent import InstagramAgent
from .content_transformer_agent import ContentTransformerAgent
from .twitter_agent import TwitterAgent
from .linkedin_agent import LinkedInAgent
from config import settings

class OrchestratorAgent:
    """Main orchestrator agent that coordinates the entire workflow"""
    
    def __init__(self):
        # Initialize all agents
        self.instagram_agent = InstagramAgent()
        self.content_transformer = ContentTransformerAgent()
        self.twitter_agent = TwitterAgent()
        self.linkedin_agent = LinkedInAgent()
        
        # Define the orchestrator agent
        self.agent = Agent(
            role="Content Workflow Orchestrator",
            goal="Coordinate the entire Instagram-to-Social Media transformation workflow",
            backstory="""You are the master coordinator of a sophisticated content 
            transformation system. You oversee the extraction of Instagram content,
            its transformation for different platforms, and the strategic posting
            across social media channels. You ensure quality, timing, and maximum
            engagement across all platforms.""",
            verbose=True,
            allow_delegation=True
        )
    
    async def execute_full_workflow(self, 
                                  target_users: List[str], 
                                  platforms: List[str] = ['twitter', 'linkedin'],
                                  schedule_posts: bool = False) -> Dict:
        """
        Execute the complete workflow from Instagram extraction to social media posting
        
        Args:
            target_users: List of Instagram usernames to extract from
            platforms: Target platforms for posting
            schedule_posts: Whether to schedule posts or post immediately
            
        Returns:
            Complete workflow results
        """
        try:
            logger.info(f"Starting full workflow for users: {target_users}, platforms: {platforms}")
            
            workflow_results = {
                'start_time': datetime.now().isoformat(),
                'target_users': target_users,
                'platforms': platforms,
                'extraction_results': {},
                'transformation_results': {},
                'posting_results': {},
                'errors': []
            }
            
            # Step 1: Extract Instagram content
            logger.info("Step 1: Extracting Instagram content...")
            extraction_results = await self.instagram_agent.execute_extraction(target_users)
            workflow_results['extraction_results'] = {
                'total_videos': len(extraction_results),
                'videos_by_user': self._group_by_user(extraction_results),
                'videos': extraction_results
            }
            
            if not extraction_results:
                logger.warning("No content extracted, stopping workflow")
                workflow_results['errors'].append("No content extracted from Instagram")
                return workflow_results
            
            # Step 2: Transform content for platforms
            logger.info("Step 2: Transforming content for platforms...")
            transformation_results = await self.content_transformer.execute_transformation(
                extraction_results, platforms
            )
            workflow_results['transformation_results'] = {
                'total_transformations': len(transformation_results),
                'transformations': transformation_results
            }
            
            if not transformation_results:
                logger.warning("No content transformed, stopping workflow")
                workflow_results['errors'].append("Content transformation failed")
                return workflow_results
            
            # Step 3: Post to social media platforms
            logger.info("Step 3: Posting to social media platforms...")
            posting_results = await self._execute_posting(
                transformation_results, platforms, schedule_posts
            )
            workflow_results['posting_results'] = posting_results
            
            # Step 4: Generate summary
            workflow_results['summary'] = self._generate_workflow_summary(workflow_results)
            workflow_results['end_time'] = datetime.now().isoformat()
            
            logger.info("Full workflow completed successfully")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error in full workflow: {str(e)}")
            workflow_results['errors'].append(f"Workflow error: {str(e)}")
            workflow_results['end_time'] = datetime.now().isoformat()
            return workflow_results
    
    async def _execute_posting(self, 
                             transformation_results: List[Dict], 
                             platforms: List[str],
                             schedule_posts: bool) -> Dict:
        """
        Execute posting across all platforms
        
        Args:
            transformation_results: Transformed content data
            platforms: Target platforms
            schedule_posts: Whether to schedule or post immediately
            
        Returns:
            Posting results for all platforms
        """
        posting_results = {}
        
        for platform in platforms:
            try:
                # Extract content for this platform
                platform_content = []
                for result in transformation_results:
                    if platform in result.get('transformed_content', {}):
                        platform_content.append(result['transformed_content'][platform])
                
                if not platform_content:
                    logger.warning(f"No content available for {platform}")
                    continue
                
                # Post to platform
                if platform == 'twitter':
                    if schedule_posts:
                        # Schedule posts with intervals
                        results = await self._schedule_twitter_posts(platform_content)
                    else:
                        results = await self.twitter_agent.execute_posting(platform_content)
                    posting_results['twitter'] = results
                    
                elif platform == 'linkedin':
                    if schedule_posts:
                        # Schedule posts with intervals
                        results = await self._schedule_linkedin_posts(platform_content)
                    else:
                        results = await self.linkedin_agent.execute_posting(platform_content)
                    posting_results['linkedin'] = results
                
            except Exception as e:
                logger.error(f"Error posting to {platform}: {str(e)}")
                posting_results[platform] = {'error': str(e)}
        
        return posting_results
    
    async def _schedule_twitter_posts(self, content_list: List[Dict]) -> List[Dict]:
        """Schedule Twitter posts with optimal timing"""
        results = []
        base_time = datetime.now() + timedelta(hours=1)  # Start in 1 hour
        
        for i, content in enumerate(content_list):
            # Schedule posts 30 minutes apart
            schedule_time = base_time + timedelta(minutes=30 * i)
            result = await self.twitter_agent.schedule_post(content, schedule_time.isoformat())
            results.append(result)
        
        return results
    
    async def _schedule_linkedin_posts(self, content_list: List[Dict]) -> List[Dict]:
        """Schedule LinkedIn posts with optimal timing"""
        results = []
        base_time = datetime.now() + timedelta(hours=2)  # Start in 2 hours
        
        for i, content in enumerate(content_list):
            # Schedule posts 2 hours apart for LinkedIn
            schedule_time = base_time + timedelta(hours=2 * i)
            result = await self.linkedin_agent.schedule_post(content, schedule_time.isoformat())
            results.append(result)
        
        return results
    
    def _group_by_user(self, extraction_results: List[Dict]) -> Dict:
        """Group extraction results by Instagram user"""
        grouped = {}
        for video in extraction_results:
            username = video.get('username', 'unknown')
            if username not in grouped:
                grouped[username] = []
            grouped[username].append(video['id'])
        return grouped
    
    def _generate_workflow_summary(self, workflow_results: Dict) -> Dict:
        """Generate a summary of the workflow execution"""
        summary = {
            'total_users_processed': len(workflow_results['target_users']),
            'total_videos_extracted': workflow_results['extraction_results'].get('total_videos', 0),
            'total_transformations': workflow_results['transformation_results'].get('total_transformations', 0),
            'posting_summary': {},
            'success_rate': {},
            'errors_count': len(workflow_results['errors'])
        }
        
        # Calculate posting success rates
        for platform, results in workflow_results['posting_results'].items():
            if isinstance(results, list):
                successful = len([r for r in results if r.get('success')])
                total = len(results)
                summary['posting_summary'][platform] = {
                    'successful': successful,
                    'total': total,
                    'success_rate': (successful / total * 100) if total > 0 else 0
                }
        
        return summary
    
    def create_workflow_crew(self, target_users: List[str], platforms: List[str]) -> Crew:
        """
        Create a CrewAI crew for the complete workflow
        
        Args:
            target_users: Instagram users to target
            platforms: Social media platforms to post to
            
        Returns:
            CrewAI Crew object
        """
        # Create tasks for each agent
        extraction_task = self.instagram_agent.create_extraction_task(target_users)
        
        # Note: These tasks will be chained together
        transformation_task = Task(
            description=f"Transform extracted content for {', '.join(platforms)}",
            agent=self.content_transformer.agent,
            expected_output="Transformed content for all platforms"
        )
        
        posting_tasks = []
        if 'twitter' in platforms:
            posting_tasks.append(self.twitter_agent.create_posting_task([]))
        if 'linkedin' in platforms:
            posting_tasks.append(self.linkedin_agent.create_posting_task([]))
        
        # Create the crew
        all_tasks = [extraction_task, transformation_task] + posting_tasks
        all_agents = [
            self.instagram_agent.agent,
            self.content_transformer.agent,
            self.twitter_agent.agent,
            self.linkedin_agent.agent,
            self.agent
        ]
        
        crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            verbose=True
        )
        
        return crew
    
    async def monitor_engagement(self, workflow_results: Dict) -> Dict:
        """
        Monitor engagement metrics for posted content
        
        Args:
            workflow_results: Results from workflow execution
            
        Returns:
            Engagement metrics
        """
        try:
            engagement_data = {}
            
            # Get Twitter engagement
            twitter_results = workflow_results.get('posting_results', {}).get('twitter', [])
            twitter_ids = [r.get('tweet_id') for r in twitter_results if r.get('success')]
            if twitter_ids:
                twitter_metrics = await self.twitter_agent.get_engagement_metrics(twitter_ids)
                engagement_data['twitter'] = twitter_metrics
            
            # Get LinkedIn engagement
            linkedin_results = workflow_results.get('posting_results', {}).get('linkedin', [])
            linkedin_ids = [r.get('post_id') for r in linkedin_results if r.get('success')]
            if linkedin_ids:
                linkedin_metrics = await self.linkedin_agent.get_engagement_metrics(linkedin_ids)
                engagement_data['linkedin'] = linkedin_metrics
            
            return engagement_data
            
        except Exception as e:
            logger.error(f"Error monitoring engagement: {str(e)}")
            return {}
