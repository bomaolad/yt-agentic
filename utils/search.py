from duckduckgo_search import DDGS


search_topic = lambda topic, num_results=10: DDGS().text(topic, max_results=num_results)


format_search_results = lambda results: "\n\n".join([
    f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}"
    for result in results
])
