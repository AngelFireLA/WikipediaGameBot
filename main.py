import asyncio
import time

import aiohttp
import os
import json
import datetime
import hashlib
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini with your API key
GENAI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GENAI_API_KEY)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
MAX_RETRIES = 5  # for handling 429 responses


#############################
# Wikipedia API Functionality
#############################

async def get_links_from_page(page_title, session, cache, semaphore):
    """
    Asynchronously fetch all internal Wikipedia links for a given page title.
    Uses caching to avoid repeated requests and a semaphore to limit concurrency.
    """
    if page_title in cache:
        return cache[page_title]

    links = set()
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "links",
        "pllimit": "max"
    }

    while True:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            async with semaphore:
                async with session.get(WIKIPEDIA_API_URL, params=params) as response:
                    if response.status == 429:
                        retry_count += 1
                        wait_time = 2 ** retry_count  # exponential backoff
                        print(f"Received 429 for '{page_title}'. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                    elif response.status != 200:
                        response.raise_for_status()

                    try:
                        data = await response.json()
                    except Exception as e:
                        print(f"Error decoding JSON for page: {page_title}")
                        raise e
                    break  # Break out if successful
        else:
            raise Exception(f"Max retries exceeded for {page_title}")

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "links" in page_data:
                for link in page_data["links"]:
                    links.add(link["title"])

        if "continue" in data:
            params.update(data["continue"])
        else:
            break
    links = list(links)
    for link in links[:]:
        if link.startswith("Help:") or link.startswith("Template:") or link.startswith("Wikipedia:") or link.startswith('Catégorie:') or link.startswith('Category:') or link.startswith('Portail:') or link.startswith('Aide:') or link.startswith('Modèle:') or link.startswith('Discussion:') or link.startswith('Fichier:') or link.startswith('File:') or link.startswith("Wikipédia:"):
            links.remove(link)
    cache[page_title] = links
    return links


#############################
# Gemini (Generative AI) Integration
#############################

async def generate_response(user_input, model_name="models/gemini-2.0-flash"):
    """
    Uses Gemini to generate a response based on the given prompt.
    The system instruction directs Gemini to act as a Wikipedia navigation assistant.
    """
    generation_config = genai.types.GenerationConfig(temperature=0)
    safety_settings = [
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    system_instruction = (
        "You are a Wikipedia navigation assistant. Given the current page, a target page, "
        "a history of visited pages, and a list of available link titles on the current page, "
        "choose exactly one link title from the list that is most likely to lead toward the target page. "
        "Respond with only the exact title of the chosen link."
    )
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        safety_settings=safety_settings,
        system_instruction=system_instruction,
    )
    prompt = [user_input]
    response = await model.generate_content_async(prompt)
    time.sleep(2)
    return response.text


async def choose_next_link(current_page, target_page, visited, available_links):
    """
    Builds a prompt with the current context and available links,
    sends it to Gemini, and returns the chosen link.
    """
    prompt = f"Current Wikipedia page: '{current_page}'\n"
    prompt += f"Target Wikipedia page: '{target_page}'\n"
    prompt += f"Visited pages so far: {', '.join(visited)}\n"
    prompt += "Available links on the current page:\n"
    for link in available_links:
        prompt += f"- {link}\n"
    prompt += (
        "\nFrom the list above, please choose exactly one link (the title) that is the best next step "
        "to reach the target page. Respond with only the exact title."
    )

    print("\n--- Prompting Gemini ---")
    print(prompt)
    chosen_link = await generate_response(prompt)
    chosen_link = chosen_link.strip()
    print("Gemini response:", chosen_link)
    return chosen_link


#############################
# Main Exploration Loop
#############################

async def explore_path(start_page, target_page, max_iterations=100):
    """
    Iteratively navigates from the start page toward the target page.
    At each step, the bot retrieves available links from the current page,
    lets Gemini decide which link to follow next, and then proceeds.
    """
    cache = {}
    visited = []
    current_page = start_page
    visited.append(current_page)
    path = [current_page]
    semaphore = asyncio.Semaphore(5)  # Limit concurrent Wikipedia API calls
    async with aiohttp.ClientSession() as session:
        for iteration in range(max_iterations):
            if current_page.strip().lower().replace(" ", "_") == target_page.strip().lower().replace(" ", "_"):
                print("\nTarget page reached!")
                return path

            print(f"\nIteration {iteration + 1}: Current page: '{current_page}'")
            available_links = await get_links_from_page(current_page, session, cache, semaphore)
            if not available_links:
                print(f"No available links found on page '{current_page}'. Stopping search.")
                continue

            chosen_link = await choose_next_link(current_page, target_page, visited, available_links)
            # Validate the chosen link
            if chosen_link not in available_links:
                print(f"Chosen link '{chosen_link}' not in available links.")
                # Optionally, you can try to find the best match or simply default to the first available link.
                print(f"Defaulting to first available link: '{available_links[0]}'.")
                chosen_link = available_links[0]

            current_page = chosen_link
            path.append(current_page)
            visited.append(current_page)
            print("Moving to:", current_page)

        print("\nMax iterations reached or target not found.")
        return path


#############################
# Main Entry Point
#############################

def main():
    start_page = "Pizza"
    target_page = "Chocolate"
    print(f"\nStarting exploration from '{start_page}' towards '{target_page}'...")

    path = asyncio.run(explore_path(start_page, target_page))
    print("\nExploration path:")
    print(" -> ".join(path))


if __name__ == '__main__':
    main()
