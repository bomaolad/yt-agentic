import os
import re
from utils.search import search_topic, format_search_results
from utils.gemini import generate_script


ensure_output_dir = lambda: os.makedirs("output", exist_ok=True)

sanitize_filename = lambda topic: re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:50]

save_script = lambda topic, script: (
    ensure_output_dir(),
    open(f"output/{sanitize_filename(topic)}_script.txt", "w").write(script)
)[1]


run_agent = lambda topic: (
    print(f"\n🔍 Searching for information on: {topic}"),
    (search_results := search_topic(topic)),
    print(f"✅ Found {len(search_results)} search results"),
    (formatted_results := format_search_results(search_results)),
    print("\n🤖 Generating script with Gemini..."),
    (script := generate_script(topic, formatted_results)),
    print("✅ Script generated successfully"),
    (filepath := f"output/{sanitize_filename(topic)}_script.txt"),
    save_script(topic, script),
    print(f"\n📄 Script saved to: {filepath}"),
    print("\n" + "="*50),
    print("GENERATED SCRIPT PREVIEW:"),
    print("="*50),
    print(script[:500] + "..." if len(script) > 500 else script),
    script
)[-1]


if __name__ == "__main__":
    topic = input("\n🎬 Enter your YouTube video topic: ").strip()
    
    if not topic:
        print("❌ Please provide a topic")
        exit(1)
    
    run_agent(topic)
