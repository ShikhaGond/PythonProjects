import requests
import json
import os
from dotenv import load_dotenv
import argparse

class IMDbRatingsFinder:
    """A class to find IMDb ratings for movies and TV shows using the OMDb API."""
    
    def __init__(self, api_key=None):
        """Initialize the IMDbRatingsFinder with an API key."""
        # Load API key from environment variable or use provided key
        load_dotenv()
        self.api_key = api_key or os.getenv("OMDB_API_KEY")
        self.base_url = "http://www.omdbapi.com/"
        
        if not self.api_key:
            print("Warning: No API key provided. Get a free API key at http://www.omdbapi.com/apikey.aspx")
    
    def search_by_title(self, title, year=None):
        """Search for movies/shows by title and optionally by year."""
        params = {
            'apikey': self.api_key,
            's': title,
            'type': 'movie,series'
        }
        
        if year:
            params['y'] = year
            
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                return data.get('Search', [])
            else:
                print(f"Error: {data.get('Error', 'Unknown error')}")
                return []
        else:
            print(f"Error: HTTP Status {response.status_code}")
            return []
    
    def get_details(self, imdb_id=None, title=None, year=None):
        """Get detailed information including ratings for a movie or show."""
        params = {'apikey': self.api_key}
        
        if imdb_id:
            params['i'] = imdb_id
        elif title:
            params['t'] = title
            if year:
                params['y'] = year
        else:
            print("Error: Either IMDb ID or title must be provided")
            return None
            
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                return data
            else:
                print(f"Error: {data.get('Error', 'Unknown error')}")
                return None
        else:
            print(f"Error: HTTP Status {response.status_code}")
            return None
    
    def display_results(self, results):
        """Display search results in a readable format."""
        if not results:
            print("No results found.")
            return
            
        print(f"\nFound {len(results)} results:")
        print("-" * 50)
        
        for i, item in enumerate(results, 1):
            print(f"{i}. {item.get('Title')} ({item.get('Year')}) - {item.get('Type')}")
            print(f"   IMDb ID: {item.get('imdbID')}")
            print()
    
    def display_details(self, details):
        """Display detailed information in a readable format."""
        if not details:
            return
            
        print("\n" + "=" * 50)
        print(f"Title: {details.get('Title')}")
        print(f"Year: {details.get('Year')}")
        print(f"Rated: {details.get('Rated')}")
        print(f"Released: {details.get('Released')}")
        print(f"Runtime: {details.get('Runtime')}")
        print(f"Genre: {details.get('Genre')}")
        print(f"Director: {details.get('Director')}")
        print(f"Writer: {details.get('Writer')}")
        print(f"Actors: {details.get('Actors')}")
        print(f"Plot: {details.get('Plot')}")
        
        print("\nRatings:")
        for rating in details.get('Ratings', []):
            print(f"- {rating.get('Source')}: {rating.get('Value')}")
            
        print(f"IMDb Rating: {details.get('imdbRating')} (from {details.get('imdbVotes')} votes)")
        print(f"IMDb ID: {details.get('imdbID')}")
        print(f"Type: {details.get('Type')}")
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Find IMDb ratings for movies and TV shows')
    parser.add_argument('--title', '-t', help='Title to search for')
    parser.add_argument('--year', '-y', help='Year of release (optional)')
    parser.add_argument('--id', '-i', help='IMDb ID (if known)')
    parser.add_argument('--api-key', '-k', help='OMDb API key (optional if set in .env file)')
    
    args = parser.parse_args()
    
    finder = IMDbRatingsFinder(api_key=args.api_key)
    
    if args.id:
        # Get details directly using IMDb ID
        details = finder.get_details(imdb_id=args.id)
        finder.display_details(details)
    elif args.title:
        # Search for title and then get details
        print(f"Searching for '{args.title}'...")
        results = finder.search_by_title(args.title, args.year)
        
        if results:
            finder.display_results(results)
            
            try:
                choice = input("\nEnter the number of the movie/show for more details (or press Enter to exit): ")
                if choice.strip():
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        imdb_id = results[idx].get('imdbID')
                        details = finder.get_details(imdb_id=imdb_id)
                        finder.display_details(details)
                    else:
                        print("Invalid selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()