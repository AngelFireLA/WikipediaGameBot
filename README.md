# Wikipedia-Game Bot

## Overview
Wikipedia Pathfinder is an AI-powered tool that navigates Wikipedia pages to find a path between a starting page and a target page. It leverages asynchronous API calls and Google's Gemini AI to intelligently choose the best path through Wikipedia.

## Features
- **Asynchronous Wikipedia API Calls:** Utilizes `aiohttp` for efficient data retrieval.
- **AI-Powered Link Selection:** Integrates Google Gemini (via the `google.generativeai` library) to decide the next best link.
- **Exponential Backoff Retry:** Implements a retry mechanism to handle Wikipedia's rate limits (HTTP 429 responses).
- **Dead Link Filtering:** Detects and filters out links that lead to dead ends.
- **Concurrency Control:** Uses asyncio semaphores to limit the number of concurrent API calls.
- **Caching Mechanism:** Caches API responses to reduce redundant requests.
- **Visited Links Exclusion:** Optionally excludes already visited pages from future link choices.
- **Custom Wiki Support:** Easily adaptable for exploring Wikipedia in different languages or alternative sites.

## Installation

### Prerequisites
- Python 3.8+
- A Google Gemini API key (to be stored in a `.env` file)
- Required dependencies (to be installed manually as there is no `requirements.txt` file)

### Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo/wikipedia-pathfinder.git
   cd wikipedia-pathfinder
   ```
2. **Install dependencies:**
   ```sh
   pip install aiohttp python-dotenv google-generativeai
   ```
3. **Create a `.env` file** in the root directory and add your API key:
   ```sh
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
Run the script using:
```sh
python main.py
```
By default, the script explores a path from **Pikachuz4** to **Biscquill**. To explore different paths, modify the `start_page` and `target_page` values in the `main()` function.

## How It Works
1. **Fetch Links:**  
   The script retrieves all internal links from the current Wikipedia page using asynchronous API calls. It caches results to avoid repeated requests.
2. **Dead Link Filtering:**  
   Before making an AI decision, the script filters out links that are considered dead (i.e., links leading to pages with no additional links or pages that only link back to the current page).
3. **AI Decision:**  
   A detailed prompt including the current page, target page, and visited pages is sent to Google Gemini. After a brief delay, Gemini responds with the optimal next link.
4. **Iteration:**  
   The process repeats until the target page is reached or the maximum number of iterations is exceeded.
5. **Output:**  
   The final navigation path is displayed in the console.

## Configuration Options
- **EXCLUDE_VISITED_LINKS:**  
  Set to `True` to exclude links that have already been visited (default), or set to `False` to allow revisiting pages.
  
- **MAX_RETRIES:**  
  Controls the number of retries on receiving a 429 (Too Many Requests) response from the Wikipedia API, with an exponential backoff strategy.
