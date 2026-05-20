import os
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

def main():
    console = Console()
    
    # Title Header
    console.print(Panel(Text("YouTube Media Downloader - Metadata Fetcher", style="bold cyan", justify="center")))
    
    # Copyright & Legal Disclaimer
    disclaimer_text = (
        "[bold yellow]Disclaimer & Legal Notice:[/bold yellow]\n"
        "This script is for personal use and educational purposes only. It is [bold red]NOT[/bold red] intended "
        "for downloading copyrighted content. Please ensure you have the legal rights, permissions, or "
        "explicit authorization from the content creator/owner before downloading or using any media assets directly from YouTube."
    )
    console.print(Panel(disclaimer_text, border_style="yellow"))
    
    # Step 1: Check for API Key in Environment Variables
    api_key = os.environ.get("RAPIDAPI_KEY") or os.environ.get("YOUTUBE_MEDIA_DOWNLOADER_KEY")
    
    if not api_key:
        console.print("[bold blue]API Key not found in environment variables (RAPIDAPI_KEY or YOUTUBE_MEDIA_DOWNLOADER_KEY).[/bold blue]")
        api_key = Prompt.ask("Please enter your RapidAPI Key", password=True)
        if not api_key.strip():
            console.print("[bold red]Error: API Key cannot be empty.[/bold red]")
            return
    else:
        console.print("[bold green]✓ API Key successfully loaded from environment variables.[/bold green]")
        
    # Step 2: Request Video ID from User
    video_id = Prompt.ask("Enter the YouTube Video ID (e.g., G33j5Qi4rE8)")
    if not video_id.strip():
        console.print("[bold red]Error: Video ID cannot be empty.[/bold red]")
        return

    video_id = video_id.strip()

    # API Configuration
    url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
    querystring = {
        "videoId": video_id,
        "urlAccess": "normal",
        "videos": "auto",
        "audios": "auto"
    }
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    # Step 3: Fetch Data using rich status loading animation
    try:
        with console.status(f"[bold green]Fetching metadata for Video ID: [cyan]{video_id}[/cyan]...", spinner="dots"):
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
        
        # Validate if API layer returned an intrinsic error
        if data.get("errorId") and data.get("errorId") != "Success":
            console.print(f"[bold red]API Error: {data.get('errorId')}[/bold red]")
            return
            
        # Step 4: Write response JSON to file
        output_filename = f"results_{video_id}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        console.print(f"\n[bold green]✓ Success![/bold green] Metadata has been saved to [magenta]{output_filename}[/magenta].")
        
        # Step 5: Print a clean Summary parsing some keys from the payload
        title = data.get("title", "Unknown Title")
        channel_name = data.get("channel", {}).get("name", "Unknown Channel")
        view_count = data.get("viewCount", "Unknown")
        
        console.print("\n[bold cyan]Video Details Summary:[/bold cyan]")
        console.print(f" • [bold]Title:[/bold] {title}")
        console.print(f" • [bold]Channel:[/bold] {channel_name}")
        if isinstance(view_count, int):
            console.print(f" • [bold]Views:[/bold] {view_count:,}")
        else:
            console.print(f" • [bold]Views:[/bold] {view_count}")
        
    except requests.exceptions.HTTPError as http_err:
        console.print(f"[bold red]HTTP error occurred:[/bold red] {http_err}")
    except requests.exceptions.RequestException as req_err:
        console.print(f"[bold red]An error occurred while connecting to the API:[/bold red] {req_err}")
    except json.JSONDecodeError:
        console.print("[bold red]Failed to decode the server response as JSON.[/bold red]")

if __name__ == "__main__":
    main()