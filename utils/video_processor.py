"""
Video Processing Utilities
"""
import os
import cv2
from typing import Dict, Optional, Tuple
from moviepy.editor import VideoFileClip
from PIL import Image
from loguru import logger
from config import settings

class VideoProcessor:
    """Utility class for video processing operations"""
    
    def __init__(self):
        # Create temp directory for processing
        os.makedirs(settings.temp_path, exist_ok=True)
    
    async def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze video file and extract metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            Video analysis dictionary
        """
        try:
            logger.info(f"Analyzing video: {os.path.basename(video_path)}")
            
            # Get basic video info using OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return {}
            
            # Extract video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Use MoviePy for additional analysis
            try:
                clip = VideoFileClip(video_path)
                has_audio = clip.audio is not None
                clip.close()
            except Exception as e:
                logger.warning(f"MoviePy analysis failed: {str(e)}")
                has_audio = False
            
            video_info = {
                'file_path': video_path,
                'file_size': file_size,
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'resolution': f"{width}x{height}",
                'aspect_ratio': width / height if height > 0 else 1,
                'has_audio': has_audio,
                'format': os.path.splitext(video_path)[1].lower()
            }
            
            logger.info(f"Video analysis complete: {duration:.1f}s, {width}x{height}")
            return video_info
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            return {}
    
    async def extract_thumbnail(self, video_path: str, timestamp: float = 1.0) -> Optional[str]:
        """
        Extract thumbnail from video at specified timestamp
        
        Args:
            video_path: Path to video file
            timestamp: Time in seconds to extract thumbnail
            
        Returns:
            Path to thumbnail image or None if extraction fails
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return None
            
            # Set position to timestamp
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                logger.error("Could not extract frame from video")
                return None
            
            # Save thumbnail
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            thumbnail_path = os.path.join(settings.temp_path, f"{video_name}_thumbnail.jpg")
            
            cv2.imwrite(thumbnail_path, frame)
            
            logger.info(f"Thumbnail extracted: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail: {str(e)}")
            return None
    
    async def resize_video(self, video_path: str, target_resolution: Tuple[int, int]) -> Optional[str]:
        """
        Resize video to target resolution
        
        Args:
            video_path: Path to input video
            target_resolution: (width, height) tuple
            
        Returns:
            Path to resized video or None if resize fails
        """
        try:
            logger.info(f"Resizing video to {target_resolution}")
            
            clip = VideoFileClip(video_path)
            resized_clip = clip.resize(target_resolution)
            
            # Generate output path
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.temp_path, f"{video_name}_resized.mp4")
            
            # Write resized video
            resized_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            clip.close()
            resized_clip.close()
            
            logger.info(f"Video resized successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error resizing video: {str(e)}")
            return None
    
    async def trim_video(self, video_path: str, start_time: float, end_time: float) -> Optional[str]:
        """
        Trim video to specified time range
        
        Args:
            video_path: Path to input video
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Path to trimmed video or None if trim fails
        """
        try:
            logger.info(f"Trimming video from {start_time}s to {end_time}s")
            
            clip = VideoFileClip(video_path)
            trimmed_clip = clip.subclip(start_time, end_time)
            
            # Generate output path
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.temp_path, f"{video_name}_trimmed.mp4")
            
            # Write trimmed video
            trimmed_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            clip.close()
            trimmed_clip.close()
            
            logger.info(f"Video trimmed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error trimming video: {str(e)}")
            return None
    
    async def compress_video(self, video_path: str, target_size_mb: float) -> Optional[str]:
        """
        Compress video to target file size
        
        Args:
            video_path: Path to input video
            target_size_mb: Target file size in MB
            
        Returns:
            Path to compressed video or None if compression fails
        """
        try:
            logger.info(f"Compressing video to {target_size_mb}MB")
            
            clip = VideoFileClip(video_path)
            duration = clip.duration
            
            # Calculate target bitrate
            target_size_bits = target_size_mb * 8 * 1024 * 1024
            target_bitrate = int(target_size_bits / duration)
            
            # Generate output path
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.temp_path, f"{video_name}_compressed.mp4")
            
            # Write compressed video
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate=f"{target_bitrate}",
                verbose=False,
                logger=None
            )
            
            clip.close()
            
            logger.info(f"Video compressed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error compressing video: {str(e)}")
            return None
    
    async def convert_format(self, video_path: str, target_format: str) -> Optional[str]:
        """
        Convert video to different format
        
        Args:
            video_path: Path to input video
            target_format: Target format (e.g., 'mp4', 'avi', 'mov')
            
        Returns:
            Path to converted video or None if conversion fails
        """
        try:
            logger.info(f"Converting video to {target_format}")
            
            clip = VideoFileClip(video_path)
            
            # Generate output path
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.temp_path, f"{video_name}.{target_format}")
            
            # Write converted video
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            clip.close()
            
            logger.info(f"Video converted successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting video: {str(e)}")
            return None
    
    async def add_watermark(self, video_path: str, watermark_text: str) -> Optional[str]:
        """
        Add text watermark to video
        
        Args:
            video_path: Path to input video
            watermark_text: Text to add as watermark
            
        Returns:
            Path to watermarked video or None if operation fails
        """
        try:
            from moviepy.editor import TextClip, CompositeVideoClip
            
            logger.info(f"Adding watermark: {watermark_text}")
            
            clip = VideoFileClip(video_path)
            
            # Create text clip
            txt_clip = TextClip(
                watermark_text,
                fontsize=24,
                color='white',
                font='Arial-Bold'
            ).set_position(('right', 'bottom')).set_duration(clip.duration)
            
            # Composite video with watermark
            final_clip = CompositeVideoClip([clip, txt_clip])
            
            # Generate output path
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(settings.temp_path, f"{video_name}_watermarked.mp4")
            
            # Write watermarked video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            clip.close()
            txt_clip.close()
            final_clip.close()
            
            logger.info(f"Watermark added successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for filename in os.listdir(settings.temp_path):
                file_path = os.path.join(settings.temp_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temp file: {filename}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
