import os
import tempfile
import yt_dlp
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

from baby_shield_backend.ai import process_video


@api_view(['POST'])
def download_video(request):
    """
    API endpoint to download first 10 seconds of a video from a URL
    """
    try:
        # Get URL from request body
        url = request.data.get('url')
        
        if not url:
            return Response({
                'error': 'URL is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            print(f"Temporary directory created at: {temp_dir}")
            # Configure youtube-dl options for downloading first 10 seconds
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'external_downloader': 'ffmpeg',
                'external_downloader_args': ['-t', '5'],  # Limit to first 10 seconds
                'writesubtitles': False,
                'writeautomaticsub': False,
                'quiet': True,
                'no_warnings': True,
            }

            # if youtube, add quality check
            if "youtube.com" in url or "youtu.be" in url:
                ydl_opts['format'] = 'best[height<=720]'
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download the video (first 10 seconds)
                ydl.download([url])
                
                # List files in temp directory to confirm download
                downloaded_files = os.listdir(temp_dir)
                
            
            
            ### TODO: Send this path (video) to the multi-agent model and get the responses as below
            file_path = os.path.join(temp_dir, downloaded_files[0]) if downloaded_files else None

            data = process_video(file_path)

            print(data)
                
            ### reduceSpeed: bool (if true, fractor given in speedFactor)
            ### applyFilters: list of filters to apply ('tone-down', 'blur', 'grayscale') or empty
            ### showWarning: bool (if true, warningMessage to be shown)
            response_data = {
                'reduceSpeed': data['playback_speed_analysis']['needs_slower_playback'],
                'speedFactor': data['playback_speed_analysis']['recommended_factor'],
                'applyFilters':  ['tone-down'] if data['color_contrast_analysis'].get('needs_reduced_contrast')  else [],
                'showWarning': data['content_safety_analysis']['contains_inappropriate_content'],
                'warningMessage': data['content_safety_analysis']['safety_message'] if data['content_safety_analysis']['contains_inappropriate_content'] else '',
                # 'showWarning': True,
                # 'warningMessage': 'This video contains fast movements that may be harmful to babies.',
            }
   

            # Files are automatically cleaned up when temp directory context exits
            return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)