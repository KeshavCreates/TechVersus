import csv
from itertools import combinations
import os
import re

# 1. READ DATA
phones = []
with open('phones.csv', 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        phones.append(row)

output_folder = "content/posts"
os.makedirs(output_folder, exist_ok=True)

# --- HELPERS ---
def get_price(text):
    clean_text = re.sub(r'[^\d.]', '', text) 
    try: return float(clean_text)
    except: return 0.0

def get_number(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

def get_screen_size(text):
    match = re.search(r'\d+\.?\d*', text)
    return float(match.group()) if match else 0.0

def is_foldable(phone):
    size = get_screen_size(phone['screen_size'])
    name = phone['model_name'].lower()
    return size > 7.4 or 'fold' in name or 'flip' in name

def is_ios(phone):
    return 'apple' in phone['brand'].lower() or 'iphone' in phone['model_name'].lower()

def is_flagship_processor(proc_name):
    proc_name = proc_name.lower()
    flagships = ['snapdragon 8', 'gen 2', 'gen 3', 'apple a1', 'apple a2', 'apple a3', 'tensor g', 'exynos 2', 'exynos 4']
    return any(x in proc_name for x in flagships)

# --- INTELLIGENT WRITERS ---

def write_camera_deep_dive(phone_a, phone_b):
    mp_a = get_number(phone_a['camera_mp'])
    mp_b = get_number(phone_b['camera_mp'])
    
    if mp_a > mp_b:
        winner, loser = phone_a, phone_b
        win_mp, lose_mp = mp_a, mp_b
    else:
        winner, loser = phone_b, phone_a
        win_mp, lose_mp = mp_b, mp_a

    # Logic: Ultra High Res Winner
    if win_mp >= 108:
        if is_foldable(loser):
             return f"**The Photography King:** The **{winner['model_name']}** is the clear winner here. Its massive **{win_mp}MP** sensor is designed for extreme detail, whereas foldables like the {loser['model_name']} often compromise on camera hardware."
        elif is_ios(loser):
             return f"**Resolution vs Optimization:** The **{winner['model_name']}** wins on raw specs with its **{win_mp}MP** sensor (great for zoom). However, the **{loser['model_name']}** ({lose_mp}MP) is known for industry-leading video quality and shutter consistency. Choose the {winner['model_name']} for zoom, or the {loser['model_name']} for video."
        else:
             return f"**Detail Monster:** The **{winner['model_name']}** dominates the spec sheet with a **{win_mp}MP** sensor compared to the {lose_mp}MP on the {loser['model_name']}."

    # Logic: Expensive vs Cheap (Quality over Quantity)
    price_a = get_price(phone_a['price'])
    price_b = get_price(phone_b['price'])
    price_winner = phone_a if price_a > price_b else phone_b
    price_loser = phone_b if price_a > price_b else phone_a
    
    if get_number(price_winner['camera_mp']) < get_number(price_loser['camera_mp']) and abs(price_a - price_b) > 300:
        return f"**Quality over Quantity.** Don't let the stats fool you. While the **{price_loser['model_name']}** boasts more megapixels, the premium **{price_winner['model_name']}** uses a superior sensor. You will get better night mode and stabilization from the {price_winner['model_name']}."

    elif abs(mp_a - mp_b) >= 20:
        return f"On paper, the **{winner['model_name']}** takes the lead with a high-resolution **{win_mp}MP** main shooter."

    else:
        return f"Both devices offer comparable camera setups. The **{phone_a['model_name']}** ({mp_a}MP) and **{phone_b['model_name']}** ({mp_b}MP) will both deliver excellent daily shots."

def write_final_recommendation(phone_a, phone_b):
    price_a = get_price(phone_a['price'])
    price_b = get_price(phone_b['price'])
    diff_price = abs(price_a - price_b)
    cheaper = phone_a if price_a < price_b else phone_b
    expensive = phone_b if price_a < price_b else phone_a
    
    # --- 1. VALUE VERDICT ---
    rec_text = ""
    if diff_price > 300:
        rec_text += f"**For Value Hunters:** The **{cheaper['model_name']}** saves you a massive **${diff_price:.0f}**. Unless you absolutely need the pro-level features of the {expensive['model_name']}, the {cheaper['model_name']} is the smarter financial buy."
    else:
        rec_text += f"**For Comparisons:** With a price difference of only **${diff_price:.0f}**, your choice comes down to features rather than budget."
    
    rec_text += "\n\n"
    
    # --- 2. DYNAMIC BULLET POINT GENERATOR (THE "DIFFERENCE ENGINE") ---
    def get_buy_reason(phone, competitor):
        proc = phone['processor'].lower()
        comp_proc = competitor['processor'].lower()
        screen = get_screen_size(phone['screen_size'])
        comp_screen = get_screen_size(competitor['screen_size'])
        mah = get_number(phone['battery_mah'])
        comp_mah = get_number(competitor['battery_mah'])
        
        # LOGIC 1: IDENTICAL PROCESSORS? (Avoid Duplicate Text)
        processors_are_same = proc == comp_proc
        
        # LOGIC 2: FOLDABLES (High Priority)
        if is_foldable(phone) and not is_foldable(competitor):
            return "if you want a **tablet in your pocket**. It is the ultimate multitasking tool."

        # LOGIC 3: SCREEN SIZE (If significant difference)
        # Phone is bigger
        if screen - comp_screen > 0.3:
            return f"for **media consumption**. The large **{phone['screen_size']}** display is significantly more immersive for video."
        # Phone is smaller
        if comp_screen - screen > 0.3:
            return "for **comfort**. It is significantly easier to use with one hand and fits better in pockets."

        # LOGIC 4: BATTERY (If significant difference)
        if mah - comp_mah > 400:
             return f"for **endurance**. The massive **{mah} mAh** battery will easily outlast the competition."

        # LOGIC 5: APPLE SPECIFIC (Only if Processors are DIFFERENT)
        if not processors_are_same and ('apple' in proc or 'bionic' in proc):
            return f"for **longevity**. The **{phone['processor']}** chip is unrivaled in efficiency and long-term support."

        # LOGIC 6: GAMING (Only if Processors are DIFFERENT and Flagship)
        if not processors_are_same and is_flagship_processor(phone['processor']) and not is_flagship_processor(competitor['processor']):
            return f"for **heavy gaming**. The {phone['processor']} is a powerhouse that handles 3D graphics much better than the competition."

        # LOGIC 7: PRICE (Fallback)
        p_phone = get_price(phone['price'])
        p_comp = get_price(competitor['price'])
        if p_comp - p_phone > 100:
            return f"for **value**. You get a similar experience for **${p_comp - p_phone:.0f} less**."
            
        # LOGIC 8: GENERIC FALLBACK
        return f"if you prefer the {phone['brand']} ecosystem and design."

    # Construct the bullet points
    rec_text += f"* **Choose the {phone_a['model_name']}** {get_buy_reason(phone_a, phone_b)}\n"
    rec_text += f"* **Choose the {phone_b['model_name']}** {get_buy_reason(phone_b, phone_a)}"

    return rec_text

def write_battery_analysis(phone_a, phone_b):
    mah_a = get_number(phone_a['battery_mah'])
    mah_b = get_number(phone_b['battery_mah'])
    diff = abs(mah_a - mah_b)
    winner = phone_a['model_name'] if mah_a > mah_b else phone_b['model_name']
    
    if diff > 400:
        return f"The **{winner}** is the clear endurance champion here. Its **{max(mah_a, mah_b)} mAh** cell is significantly larger than the competition."
    elif diff == 0:
        return f"It's a draw. Both devices pack a **{mah_a} mAh** battery, so expect similar endurance."
    else:
        return f"It's a tight race. The **{winner}** holds a slight edge with {max(mah_a, mah_b)} mAh, but real-world battery life will be very similar."

# 2. GENERATION LOOP
for phone_a, phone_b in combinations(phones, 2):
    
    # Add .replace("/", "") to remove slashes
    slug = f"{phone_a['model_name']}-vs-{phone_b['model_name']}".replace(" ", "-").replace("/", "").lower()
    filename = f"{output_folder}/{slug}.md"
    
    price_a = get_price(phone_a['price'])
    price_b = get_price(phone_b['price'])
    mah_a = get_number(phone_a['battery_mah'])
    mah_b = get_number(phone_b['battery_mah'])

    # Writers
    cam_deep_dive = write_camera_deep_dive(phone_a, phone_b)
    bat_analysis = write_battery_analysis(phone_a, phone_b)
    final_rec = write_final_recommendation(phone_a, phone_b)

    # Highlight Logic
    def style_winner(val_a, val_b, inverse=False):
        a = get_number(val_a) if isinstance(val_a, str) else val_a
        b = get_number(val_b) if isinstance(val_b, str) else val_b
        win_style = "color: #166534; font-weight: 700; background-color: #dcfce7; padding: 2px 6px; border-radius: 4px;"
        
        if inverse: 
            if a < b: return (f"<span style='{win_style}'>${val_a}</span>", f"${val_b}")
            else: return (f"${val_a}", f"<span style='{win_style}'>${val_b}</span>")
        else:
            if a > b: return (f"<span style='{win_style}'>{val_a}</span>", f"{val_b}")
            else: return (f"{val_a}", f"<span style='{win_style}'>{val_b}</span>")

    p_a_str, p_b_str = style_winner(price_a, price_b, inverse=True)
    mah_a_str, mah_b_str = style_winner(mah_a, mah_b)
    cam_a_str, cam_b_str = style_winner(phone_a['camera_mp'], phone_b['camera_mp'])

    def format_verdict(text):
        # Split on newline + asterisk to separate the paragraph from bullet points
        parts = text.split('\n*')
        paragraph = parts[0].strip()
        # Replace bold markdown with html strong
        return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', paragraph)

    content = f"""---
title: "{phone_a['model_name']} vs {phone_b['model_name']}"
description: "Compare {phone_a['model_name']} vs {phone_b['model_name']} specs. Find out which phone has the better camera, battery life, and value."
date: 2024-01-01
draft: false
---

# {phone_a['model_name']} vs {phone_b['model_name']}

<div class="verdict">
    <div class="verdict-title">The Quick Verdict</div>
    {format_verdict(final_rec)}
</div>

## 📊 Specs at a Glance

| Feature | {phone_a['model_name']} | {phone_b['model_name']} |
| :--- | :--- | :--- |
| **Price** | {p_a_str} | {p_b_str} |
| **Battery** | {mah_a_str} mAh | {mah_b_str} mAh |
| **Camera** | {cam_a_str} MP | {cam_b_str} MP |
| **Screen** | {phone_a['screen_size']} | {phone_b['screen_size']} |
| **Processor** | {phone_a['processor']} | {phone_b['processor']} |

## 📸 Camera Specs
{cam_deep_dive}

## 🔋 Battery Capacity
{bat_analysis}

## 💡 Which one is right for you?

{final_rec}
"""
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(content)

print("Success! Duplicate processor logic removed. Recommendations now weigh screen, battery, and price.")