#!/usr/bin/env python3
"""
Test script to verify Y4M file and create a simple test video if needed
"""
import os

def check_y4m_file(file_path):
    """Check if Y4M file exists and is valid"""
    if not os.path.exists(file_path):
        print(f"❌ Y4M file not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(10)
            if header.startswith(b'YUV4MPEG2'):
                print(f"✅ Valid Y4M file found: {file_path}")
                print(f"📊 File size: {os.path.getsize(file_path)} bytes")
                return True
            else:
                print(f"❌ Invalid Y4M file (missing YUV4MPEG2 header): {file_path}")
                return False
    except Exception as e:
        print(f"❌ Error reading Y4M file: {e}")
        return False

def create_simple_y4m(output_path):
    """Create a simple Y4M test file"""
    try:
        # Simple Y4M header for a 320x240 video at 1 fps
        header = b"YUV4MPEG2 W320 H240 F1:1 Ip A0:0 C420jpeg\n"
        frame_header = b"FRAME\n"
        
        # Create a simple frame (black frame)
        frame_size = 320 * 240 + 2 * (160 * 120)  # Y + U + V planes
        frame_data = b'\x00' * frame_size
        
        with open(output_path, 'wb') as f:
            f.write(header)
            # Write 10 frames
            for i in range(10):
                f.write(frame_header)
                f.write(frame_data)
        
        print(f"✅ Created simple Y4M test file: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating Y4M file: {e}")
        return False

if __name__ == "__main__":
    y4m_path = "/Users/pratik/Downloads/Assesment/mcp_ai_testAgent/sample.y4m"
    
    print("🎥 Y4M File Checker")
    print("=" * 30)
    
    if not check_y4m_file(y4m_path):
        print("\n🔧 Creating test Y4M file...")
        if create_simple_y4m(y4m_path):
            check_y4m_file(y4m_path)
    
    print("\n📋 Browser Arguments for Y4M:")
    print(f"--use-file-for-fake-video-capture={y4m_path}")
    print("--use-fake-ui-for-media-stream")
    print("--use-fake-device-for-media-stream")