import subprocess
import json
import os
import re
from yt_dlp import YoutubeDL
import google.generativeai as genai


def search_youtube(keyword, max_results=4):
    cmd = ["yt-dlp", f"ytsearch{max_results}:{keyword}", "--print-json", "--skip-download"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    videos = [json.loads(line) for line in result.stdout.strip().split('\n')]
    return videos

def clean_subtitle_text(subtitle_text: str) -> str:
    """
    Removes timestamps and line numbers from an .srt subtitle string.
    Returns the cleaned plain text.
    """
    # Remove subtitle indices (lines with only a number)
    no_indices = re.sub(r'^\d+\s*$', '', subtitle_text, flags=re.MULTILINE)
    
    # Remove timestamp lines
    no_timestamps = re.sub(r'^\d{2}:\d{2}:\d{2},\d{3} --> .*$', '', no_indices, flags=re.MULTILINE)
    
    # Remove extra blank lines
    cleaned = re.sub(r'\n+', '\n', no_timestamps).strip()
    
    return cleaned

def download_transcript(video_id):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'srt',
        'outtmpl': '%(id)s.%(ext)s'
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            srt_file = f"{video_id}.en.srt"
            if os.path.exists(srt_file):
                with open(srt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                os.remove(srt_file)
                return clean_subtitle_text(content)
        except Exception as e:
            print(f"Failed to get transcript for video {video_id}: {e}")
    return None

def save_transcripts(keyword, videos):
    output_file = f"{keyword.replace(' ', '_')}_transcripts.txt"
    with open(output_file, 'w', encoding='utf-8') as out:
        for video in videos:
            video_id = video.get('id')
            title = video.get('title')
            transcript = download_transcript(video_id)
            out.write(f"\n=== {title} ===\n\n")
            if transcript:
                out.write(transcript + "\n")
            else:
                out.write("Transcript not available.\n")
    print(f"\n✅ Transcripts saved to: {output_file}")


def summarize_transcript_with_gemini(cleaned_transcript: str, api_key: str,company_name: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.5-flash-lite",
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            top_p=1,
            top_k=40,
            max_output_tokens=1024
        )
    )

    prompt = (
        f'''You are given the cleaned transcript of a YouTube video related to a company.

Your task is to extract and summarize all **useful, factual information** about the company {company_name} in a structured and professional format if available. Do not assume or invent anything — base your summary only on what is explicitly stated or clearly implied.

Your output must be:

- **Comprehensive**: Include all business-relevant information (even briefly mentioned details).
- **Structured**: Organize the output using clear sections with headers.
- **Concise and readable**: Use complete sentences, avoid repetition, and ensure clarity.

Extract and organize the following if present:

1. **Company Name and Overview**  
2. **Mission and Vision**  
3. **Key Products, Services, or Solutions**  
4. **Target Markets and Industries**  
5. **Strategic Approach or Innovation Focus**  
6. **Partnerships, Clients, or Global Presence**  
7. **Events, Initiatives, or Campaigns** 
8. **Additional Insights**  

if the company is not explicitly mentioned, focus on the general context of the video and any relevant industry insights.

Make sure the summary reads like a professional profile written by a business analyst.
Do not include the original transcript.

Transcript:
{cleaned_transcript}

'''
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"


def lanceYoutubeSearch(api_key: str, keyword: str, company_name: str) -> str:
    videos = search_youtube(keyword)
    all_summaries = ""

    for video in videos:
        video_id = video.get('id')
        title = video.get('title')
        print(f"\n🔍 Processing video: {title} ({video_id})")

        transcript = download_transcript(video_id)
        if transcript:
            summary = summarize_transcript_with_gemini(transcript, api_key, company_name)
            all_summaries += f"\n\n📄 Summary for '{title}':\n{summary}\n"
        else:
            print(f"❌ Transcript not available for video: {title}")

    return all_summaries.strip()


