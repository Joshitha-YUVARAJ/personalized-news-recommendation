import os
import pandas as pd
import requests
import zipfile
import tempfile
from pathlib import Path

def create_sample_dataset():
    """Create a sample dataset with real-looking news data for demo purposes"""
    
    # Create the dataset directory
    dataset_dir = Path(__file__).parent.parent / "MINDsmall_train"
    dataset_dir.mkdir(exist_ok=True)
    
    # Sample news data with diverse categories and realistic content
    sample_news = [
        ["N1", "technology", "tech", "Apple Unveils New iPhone with Revolutionary AI Features", "The latest iPhone model includes advanced AI capabilities that promise to transform how users interact with their devices.", "https://example.com/apple-iphone", "[]", "[]"],
        ["N2", "business", "finance", "Stock Market Reaches Record High Amid Economic Recovery", "Major stock indices hit all-time highs as investors show confidence in the ongoing economic recovery efforts.", "https://example.com/stock-market", "[]", "[]"],
        ["N3", "health", "wellness", "Study Reveals Benefits of Mediterranean Diet for Heart Health", "A comprehensive study of 10,000 participants shows significant cardiovascular benefits from following a Mediterranean diet.", "https://example.com/mediterranean-diet", "[]", "[]"],
        ["N4", "sports", "football", "Championship Game Draws Record Television Audience", "The season finale attracted the largest TV audience in the sport's history, with millions tuning in worldwide.", "https://example.com/championship", "[]", "[]"],
        ["N5", "science", "research", "Breakthrough in Quantum Computing Brings Practical Applications Closer", "Researchers achieve a major milestone in quantum error correction, paving the way for real-world quantum computers.", "https://example.com/quantum", "[]", "[]"],
        ["N6", "entertainment", "movies", "Independent Film Festival Showcases Emerging Talent", "This year's festival highlights innovative storytelling from directors making their feature film debuts.", "https://example.com/film-festival", "[]", "[]"],
        ["N7", "politics", "policy", "New Environmental Regulations Aim to Reduce Carbon Emissions", "Government announces comprehensive plan to achieve carbon neutrality by 2050 through innovative policy measures.", "https://example.com/environment", "[]", "[]"],
        ["N8", "travel", "tourism", "Remote Destinations See Tourism Boom as Travel Resumes", "Lesser-known travel destinations experience unprecedented visitor growth as people seek unique experiences.", "https://example.com/travel", "[]", "[]"],
        ["N9", "food", "cooking", "Plant-Based Cuisine Gains Popularity in Fine Dining", "Top restaurants embrace plant-based ingredients, creating innovative dishes that rival traditional meat-centered menus.", "https://example.com/plant-based", "[]", "[]"],
        ["N10", "lifestyle", "fashion", "Sustainable Fashion Brands Lead Industry Transformation", "Eco-conscious fashion companies demonstrate that style and sustainability can go hand in hand.", "https://example.com/sustainable-fashion", "[]", "[]"],
        ["N11", "technology", "ai", "AI Assistants Become More Human-like with Latest Updates", "Natural language processing improvements make AI assistants more conversational and helpful than ever before.", "https://example.com/ai-assistants", "[]", "[]"],
        ["N12", "business", "startup", "Tech Startup Raises $50M to Develop Clean Energy Solutions", "Innovative company secures major funding to accelerate development of next-generation solar technology.", "https://example.com/startup-funding", "[]", "[]"],
        ["N13", "health", "mental-health", "Mental Health Apps Show Promise in Clinical Trials", "Digital therapy platforms demonstrate effectiveness comparable to traditional counseling in treating anxiety and depression.", "https://example.com/mental-health-apps", "[]", "[]"],
        ["N14", "sports", "olympics", "Olympic Athletes Prepare for Games with High-Tech Training", "Advanced sports science and technology help athletes optimize performance and prevent injuries.", "https://example.com/olympic-training", "[]", "[]"],
        ["N15", "science", "space", "Mars Rover Discovers Evidence of Ancient Water Systems", "Latest findings suggest Mars once had extensive river networks that could have supported life.", "https://example.com/mars-rover", "[]", "[]"],
        ["N16", "entertainment", "streaming", "Streaming Wars Heat Up with New Platform Launches", "Competition intensifies as new streaming services enter the market with exclusive content and competitive pricing.", "https://example.com/streaming-wars", "[]", "[]"],
        ["N17", "politics", "election", "Voter Turnout Reaches Historic Levels in Recent Election", "Record-breaking participation reflects increased civic engagement and accessibility of voting methods.", "https://example.com/voter-turnout", "[]", "[]"],
        ["N18", "travel", "sustainable", "Eco-Tourism Offers Sustainable Travel Alternatives", "Responsible tourism practices help protect natural environments while providing meaningful travel experiences.", "https://example.com/eco-tourism", "[]", "[]"],
        ["N19", "food", "nutrition", "Nutritionists Debunk Common Diet Myths", "Expert analysis reveals the truth behind popular diet trends and provides evidence-based nutrition guidance.", "https://example.com/diet-myths", "[]", "[]"],
        ["N20", "lifestyle", "wellness", "Meditation Apps Report Surge in Usage During Stressful Times", "Mindfulness applications see dramatic user growth as people seek stress relief and mental clarity.", "https://example.com/meditation-apps", "[]", "[]"]
    ]
    
    # Create news.tsv
    news_df = pd.DataFrame(sample_news, columns=[
        'NewsID', 'Category', 'SubCategory', 'Title', 'Abstract', 'URL', 'TitleEntities', 'AbstractEntities'
    ])
    news_df.to_csv(dataset_dir / "news.tsv", sep='\t', index=False, header=False)
    
    # Sample behaviors data
    sample_behaviors = [
        ["1", "U1", "11/15/2019 8:43:11 AM", "N1 N2", "N3-1 N4-0 N5-1"],
        ["2", "U1", "11/15/2019 9:12:34 AM", "N1 N2 N3", "N6-1 N7-0 N8-1 N9-0"],
        ["3", "U2", "11/15/2019 10:25:17 AM", "N4 N5", "N10-1 N11-1 N12-0"],
        ["4", "U2", "11/15/2019 11:43:29 AM", "N4 N5 N10", "N13-0 N14-1 N15-1"],
        ["5", "U3", "11/15/2019 12:15:42 AM", "N6 N7 N8", "N16-1 N17-0 N18-1"],
        ["6", "U3", "11/15/2019 1:33:55 PM", "N6 N7 N8 N16", "N19-1 N20-0 N1-1"],
        ["7", "U4", "11/15/2019 2:47:18 PM", "N9 N10", "N2-0 N3-1 N4-1 N5-0"],
        ["8", "U4", "11/15/2019 3:21:33 PM", "N9 N10 N2", "N11-1 N12-0 N13-1"],
        ["9", "U5", "11/15/2019 4:12:47 PM", "N11 N12 N13", "N14-0 N15-1 N16-1"],
        ["10", "U5", "11/15/2019 5:35:19 PM", "N11 N12 N13 N14", "N17-1 N18-0 N19-1 N20-0"]
    ]
    
    # Create behaviors.tsv
    behaviors_df = pd.DataFrame(sample_behaviors, columns=[
        'ImpressionID', 'UserID', 'Time', 'History', 'Impressions'
    ])
    behaviors_df.to_csv(dataset_dir / "behaviors.tsv", sep='\t', index=False, header=False)
    
    print(f"✅ Created sample dataset with {len(sample_news)} news articles and {len(sample_behaviors)} user behaviors")
    return dataset_dir

def ensure_dataset_exists():
    """Ensure dataset exists, create sample if not found"""
    dataset_dir = Path(__file__).parent.parent / "MINDsmall_train"
    
    if not dataset_dir.exists() or not (dataset_dir / "news.tsv").exists():
        print("📦 Dataset not found, creating sample dataset...")
        return create_sample_dataset()
    
    print(f"✅ Dataset found at {dataset_dir}")
    return dataset_dir

if __name__ == "__main__":
    ensure_dataset_exists()