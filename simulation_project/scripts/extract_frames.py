"""
Video Frame Extractor
Extracts frames from MP4 video for analysis
"""

import cv2
import os
from pathlib import Path


def extract_frames(video_path, output_dir=None, frame_interval=30):
    """
    Extract frames from video file
    
    Args:
        video_path: Path to MP4 file
        output_dir: Directory to save frames (default: same as video)
        frame_interval: Extract every Nth frame (default: 30 = ~1 per second at 30fps)
    
    Returns:
        List of saved frame paths
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return []
    
    # Set output directory
    if output_dir is None:
        output_dir = video_path.parent / f"{video_path.stem}_frames"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📹 Extracting frames from: {video_path.name}")
    print(f"📁 Output directory: {output_dir}")
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print("❌ Error opening video file")
        return []
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📊 Video info:")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - Total frames: {total_frames}")
    print(f"   - Duration: {duration:.2f} seconds")
    print(f"   - Extracting every {frame_interval} frames\n")
    
    saved_frames = []
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Extract every Nth frame
        if frame_count % frame_interval == 0:
            # Save frame
            frame_filename = f"frame_{extracted_count:04d}_time_{frame_count/fps:.2f}s.jpg"
            frame_path = output_dir / frame_filename
            
            cv2.imwrite(str(frame_path), frame)
            saved_frames.append(frame_path)
            extracted_count += 1
            
            print(f"✓ Extracted frame {extracted_count}: {frame_filename}")
        
        frame_count += 1
    
    cap.release()
    
    print(f"\n✅ Extraction complete!")
    print(f"   - Total frames extracted: {extracted_count}")
    print(f"   - Saved to: {output_dir}")
    
    return saved_frames


def extract_key_frames(video_path, num_frames=10):
    """
    Extract evenly spaced key frames from video
    
    Args:
        video_path: Path to MP4 file
        num_frames: Number of frames to extract
    
    Returns:
        List of saved frame paths
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return []
    
    output_dir = video_path.parent / f"{video_path.stem}_keyframes"
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📹 Extracting {num_frames} key frames from: {video_path.name}")
    
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print("❌ Error opening video file")
        return []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate frame indices to extract
    if num_frames >= total_frames:
        frame_indices = list(range(total_frames))
    else:
        frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    
    print(f"📊 Extracting frames at indices: {frame_indices[:5]}{'...' if len(frame_indices) > 5 else ''}")
    
    saved_frames = []
    
    for idx, frame_idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if ret:
            timestamp = frame_idx / fps if fps > 0 else 0
            frame_filename = f"keyframe_{idx:02d}_time_{timestamp:.2f}s.jpg"
            frame_path = output_dir / frame_filename
            
            cv2.imwrite(str(frame_path), frame)
            saved_frames.append(frame_path)
            
            print(f"✓ Extracted key frame {idx + 1}/{num_frames}: {frame_filename}")
    
    cap.release()
    
    print(f"\n✅ Extraction complete!")
    print(f"   - Saved to: {output_dir}")
    
    return saved_frames


if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) < 2:
        print("\n📹 Video Frame Extractor")
        print("\nUsage:")
        print("  python extract_frames.py <video_path> [mode]")
        print("\nModes:")
        print("  all    - Extract every 30th frame (default)")
        print("  key    - Extract 10 evenly spaced key frames")
        print("\nExample:")
        print('  python extract_frames.py "C:\\Users\\rhode\\AppData\\Local\\Packages\\...\\video.mp4" key')
        sys.exit(0)
    
    video_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    if mode == "key":
        frames = extract_key_frames(video_path, num_frames=10)
    else:
        frames = extract_frames(video_path, frame_interval=30)
    
    print(f"\n📁 You can now view the frames at:")
    if frames:
        print(f"   {frames[0].parent}")
