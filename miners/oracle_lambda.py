import requests
import json
from datetime import datetime

# --- Configuration ---
EPIC_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

def lambda_handler(event, context):
    """
    AWS Lambda Entry Point.
    Wakes up, checks the future, returns a forecast.
    """
    print("🔮 Oracle: Gazing into the future timeline...")
    
    try:
        # 1. Connect to Epic
        response = requests.get(EPIC_URL, timeout=10)
        data = response.json()
        games = data['data']['Catalog']['searchStore']['elements']
        
        forecast_list = []
        
        # 2. Analyze Data
        for game in games:
            title = game.get('title', 'Unknown Game')
            promotions = game.get('promotions')
            
            if not promotions:
                continue
            
            # --- THE PREDICTION ENGINE ---
            # Ignore current offers, look for 'upcomingPromotionalOffers'
            upcoming = promotions.get('upcomingPromotionalOffers')
            
            if upcoming:
                # Epic structure: upcoming -> list -> promotionalOffers -> list
                offers = upcoming[0]['promotionalOffers']
                
                for offer in offers:
                    # Check: Is it going to be 100% Free?
                    discount = offer['discountSetting']['discountPercentage']
                    
                    if discount == 0:
                        # Extract Time
                        start_date_str = offer['startDate']
                        
                        # Format Time (Z -> UTC)
                        try:
                            start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                            formatted_date = start_dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            formatted_date = start_date_str
                        
                        # Extract Value
                        try:
                            original_price = game['price']['totalPrice']['fmtPrice']['originalPrice']
                        except:
                            original_price = "Unknown Value"

                        # Build Intel Package
                        intel = {
                            "game": title,
                            "unlocks_at": formatted_date,
                            "value": original_price,
                            "image": game['keyImages'][0]['url'] if game.get('keyImages') else None
                        }
                        forecast_list.append(intel)
        
        # Return Forecast
        return {
            'statusCode': 200,
            'body': json.dumps(forecast_list),
            'count': len(forecast_list)
        }

    except Exception as e:
        print(f"❌ Oracle Blinded: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }

# --- Local Testing Block ---
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    # Simulate Lambda Trigger
    result = lambda_handler(None, None)
    
    if result['statusCode'] == 200:
        forecast = json.loads(result['body'])
        
        print("\n")
        if not forecast:
            console.print("[yellow]🔮 The mists are thick... No future games detected right now.[/yellow]")
        else:
            table = Table(title="[bold purple]🔮 THE ORACLE: FUTURE DROPS REVEALED[/bold purple]", border_style="purple")
            table.add_column("Game Title", style="bold white")
            table.add_column("Unlocks At (UTC)", style="cyan")
            table.add_column("Predicted Value", style="green")
            
            for item in forecast:
                table.add_row(
                    item['game'],
                    item['unlocks_at'],
                    item['value']
                )
            
            console.print(table)
            console.print(f"\n[italic grey50]Detected {len(forecast)} incoming signals.[/italic grey50]")
    else:
        console.print("[bold red]System Failure.[/bold red]")
