import os
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

# Initialize the Rich console
console = Console()

def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and accessible in the system PATH."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return True
    except FileNotFoundError:
        return False

def merge_media(video_path: str, audio_path: str, output_path: str):
    """Merges video and audio using FFmpeg without re-encoding."""
    # -c:v copy and -c:a copy ensure no re-encoding takes place
    # -map 0:v grabs the video from the first input (the mp4)
    # -map 1:a grabs the audio from the second input (the m4a)
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "copy",
        "-map", "0:v:0", # Use the first video stream from the first input
        "-map", "1:a:0", # Use the first audio stream from the second input
        "-shortest",     # Finish encoding when the shortest input stream ends
        output_path
    ]

    # Use Rich's status spinner while the subprocess runs
    with console.status("[bold cyan]Merging tracks... Please wait![/bold cyan]", spinner="bouncingBar"):
        try:
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"\n[bold green]✓ Success![/bold green] File saved to: [bold underline]{output_path}[/bold underline]")
            else:
                console.print("\n[bold red]✗ An error occurred during the FFmpeg process:[/bold red]")
                console.print(result.stderr)
                
        except Exception as e:
            console.print(f"\n[bold red]✗ Script execution error:[/bold red] {e}")

def main():
    # Display a beautiful header
    console.print(Panel.fit(
        "[bold magenta]Audio & Video Merger[/bold magenta]\n"
        "[dim]Merge MP4 and M4A streams instantly with absolutely zero re-encoding.[/dim]",
        border_style="cyan"
    ))

    if not check_ffmpeg_installed():
        console.print("[bold red]Error:[/bold red] FFmpeg is not installed or not found in your system's PATH.")
        console.print("Please install FFmpeg to use this script.")
        return

    # Interactive prompts using Rich
    video_path = Prompt.ask("\n[bold yellow]🎬 Drag & drop or type the path to your Video file (.mp4)[/bold yellow]")
    
    # Strip quotes in case the user dragged and dropped the file into the terminal
    video_path = video_path.strip("\"'") 
    
    if not os.path.isfile(video_path):
        console.print(f"[bold red]✗ Video file not found at:[/bold red] {video_path}")
        return

    audio_path = Prompt.ask("[bold yellow]🎵 Drag & drop or type the path to your Audio file (.m4a)[/bold yellow]")
    audio_path = audio_path.strip("\"'")
    
    if not os.path.isfile(audio_path):
        console.print(f"[bold red]✗ Audio file not found at:[/bold red] {audio_path}")
        return

    output_path = Prompt.ask(
        "[bold yellow]💾 Enter the desired output filename[/bold yellow]", 
        default="final_merged_output.mp4"
    )

    # Execute the merge
    merge_media(video_path, audio_path, output_path)

if __name__ == "__main__":
    main()