def small_sample():
    DOWNLOAD_DIR = "nbaDownloads"
    video_clips = []
    for i in range(0,1):
        filename = f"{DOWNLOAD_DIR}/clip_{i}.mp4"
        clip = VideoFileClip(filename, target_resolution=(1280,720))
        video_clips.append(clip)

    if video_clips:
        print("🎬 Concatenating clips...")
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(
            "highlight_compilation_small.mp4",
            codec="libx264",
            bitrate="5000k",
            preset="medium",
            audio_codec="aac",
            fps=30
        )
        print("✅ Compilation done: highlight_compilation_small.mp4")
    else:
        print("⚠️ No clips to compile.")




        # Compile the clips into one video
    # if video_clips:
    #     video_clips_small = video_clips[0:2] #small sample size of video clips
    #     print("🎬 Concatenating clips...")
    #     final_clip = concatenate_videoclips(video_clips_small, method="compose")
    #     final_clip.write_videofile(
    #         "highlight_compilation.mp4",
    #         codec="libx264",
    #         bitrate="5000k",
    #         preset="medium",
    #         audio_codec="aac",
    #         fps=30
    #     )
    #     print("✅ Compilation done: highlight_compilation.mp4")
    # else:
    #     print("⚠️ No clips to compile.")