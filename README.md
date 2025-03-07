# Wikipedia Pathfinder

## Overview
Wikipedia Pathfinder is an AI-powered tool that navigates Wikipedia pages to find a path between a starting page and a target page. It uses the Wikipedia API to fetch links from pages and Google's Gemini AI model to intelligently choose the best path to the target page.

## Features
- **Asynchronous Wikipedia API calls** for efficient data retrieval.
- **AI-powered link selection** using Google Gemini.
- **Retry mechanism** for handling Wikipedia's rate limits (429 responses).
- **Customizable start and target pages** for flexible exploration.
- **Caching mechanism** to optimize API calls and reduce redundant requests.
- **Custom Wiki support** for exploring other Wikipedia languages or sites.
## Installation
### Prerequisites
- Python 3.8+
- A Google Gemini API key (stored in a `.env` file)
- Required dependencies (install manually as there is no `requirements.txt` file)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/wikipedia-pathfinder.git
   cd wikipedia-pathfinder
   ```
2. Install dependencies:
   ```sh
   pip install aiohttp python-dotenv google-generativeai
   ```
3. Create a `.env` file in the root directory and add your API key:
   ```sh
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
Run the script with:
```sh
python main.py
```

By default, the script explores a path from Word1 to Word2. Modify `start_page` and `target_page` in `main()` to explore different paths.

## How It Works
1. **Fetch Links**: The script retrieves all internal links from the current Wikipedia page using the Wikipedia API.
2. **AI Decision**: Google Gemini selects the next best link to follow based on the given context.
3. **Iteration**: The script repeats this process until it reaches the target page or exceeds the maximum iterations.
4. **Output**: The final path is displayed in the console.

## Notes
- The AI may occasionally choose links that do not exist in the available options, in which case the first available link is used as a fallback.
- The script will stop if it reaches a page with no links or if it exceeds the maximum iterations.

## Contributing
Feel free to open issues or submit pull requests to improve functionality.