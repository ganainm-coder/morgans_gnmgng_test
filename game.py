# Spelets logik är Python! PyScript kör koden direkt i webbläsaren.
import random
from js import document
from pyodide.ffi import create_proxy

HJALTAR = {
    "riddare": {"name": "Riddaren", "emoji": "🛡️", "hp": 14},
    "magiker": {"name": "Magikern", "emoji": "🪄", "hp": 10},
    "skogsvän": {"name": "Skogsvännen", "emoji": "🏹", "hp": 12},
}

state = {"hero": None, "xp": 0, "coins": 0, "items": [], "scene": "start", "last_roll": 1, "seen": set()}
callbacks = []

SCENES = {
    "start": {
        "tag": "KAPITEL 1 · SKOGENS KANT", "title": "Ett märkligt uppdrag", "art": "🌲 🌙 🌲",
        "text": "Byns stjärna har försvunnit! Utan den lyser inte nattlamporna och de små drakungarna hittar inte hem. Spår leder in i den viskande skogen. En uggla med runda glasögon landar på en gren.\n\n”Jag såg något glittra vid den gamla bron”, hoar den. ”Men bron vaktas av en ganska lättskrämd trollunge.”",
        "choices": [("🌉", "Gå direkt till den gamla bron", "bridge"), ("🦉", "Fråga ugglan om fler ledtrådar", "owl"), ("🎒", "Titta i ryggsäcken", "bag")]
    },
    "owl": {
        "tag": "EN VÄNLIG LEDTRÅD", "title": "Ugglans hemlighet", "art": "🦉 ✨ 🌿",
        "text": "Ugglan putsar sina glasögon. ”Trollungen älskar blåbär. Och den lilla draken? Den är nog inte elak, bara ensam.” Den ger dig en blank fjäder som sägs ge lite tur.",
        "choices": [("🌉", "Tacka ugglan och gå till bron", "bridge"), ("🫐", "Leta efter blåbär att ta med", "berries"), ("↩️", "Gå tillbaka till skogsstigen", "start")]
    },
    "berries": {
        "tag": "SKOGENS SKAFFERI", "title": "Blåbär i mängder!", "art": "🫐 🍃 🫐",
        "text": "Du hittar ett helt snår av blåbär och plockar en handfull till någon som kan behöva ett mellanmål.",
        "choices": [("🌉", "Fortsätt till bron", "bridge"), ("🎒", "Kolla vad du har samlat", "bag")]
    },
    "bag": {
        "tag": "DIN RYGGSÄCK", "title": "Bra att vara förberedd", "art": "🎒 🧭 🧪",
        "text": lambda: "Du har med dig: " + ", ".join(state["items"]) + "." if state["items"] else "Din ryggsäck är tom än så länge. Men äventyret har bara börjat!",
        "choices": [("🌉", "Fortsätt till den gamla bron", "bridge"), ("↩️", "Tillbaka till stigen", "start")]
    },
    "bridge": {
        "tag": "KAPITEL 2 · DEN GAMLA BRON", "title": "Trollungen vid bron", "art": "🌉 🧌 🍄",
        "text": "På bron sitter en liten trollunge med grön mössa. ”Ingen får passera!” säger den och försöker se farlig ut. Magen kurrar så högt att en groda hoppar till. Du anar att det finns fler sätt att lösa detta än att slåss.",
        "choices": [("💬", "Prata snällt med trollungen", "talk"), ("🎲", "Hitta på ett busigt trick", "trick"), ("⚔️", "Utmana trollungen på en vänskaplig duell", "fight")]
    },
    "talk": {
        "tag": "VÄNLIGHET ÄR MAGI", "title": "En oväntad vän", "art": "🧌 💚 🐸",
        "text": "Du frågar vad trollungen heter. ”Tusse”, mumlar den och slappnar av. Ni lovar att hälsa på igen. Tusse visar en hemlig stig och ger dig två guldmynt.",
        "effect": "talk", "choices": [("🪨", "Följ den hemliga stigen", "cave")]
    },
    "feed": {
        "tag": "VÄNNER OCH BLÅBÄR", "title": "Muffinsdiplomati!", "art": "🫐 🧌 💛",
        "text": "Trollungens ögon blir stora som tekoppar. Ni delar på blåbären och skrattar. Tusse släpper fram dig och visar vägen till en gömd grotta.",
        "effect": "feed", "choices": [("🪨", "Gå till den gömda grottan", "cave")]
    },
    "trick": {
        "tag": "LISTIGT TÄNKT", "title": "Grodan som distraktion", "art": "🐸 💨 🧌",
        "text": "Du ber en groda att kväka skogens mest dramatiska kväkning. Tusse börjar skratta så mycket att den glömmer att vakta bron. Du hittar ett guldmynt på stigen.",
        "effect": "trick", "choices": [("🪨", "Följ stigen till grottan", "cave")]
    },
    "fight": {
        "tag": "VÄNSKAPLIG DUELL", "title": "Mod mot mössa", "art": "🛡️ ⚔️ 🧌",
        "text": "Tusse svingar en svamp som om den vore ett svärd. Slå tärningen! En hög siffra betyder att du vinner en vänskaplig match. Ingen behöver bli skadad på riktigt.",
        "choices": [("🎲", "Slå tärningen och duellera", "duel")]
    },
    "duel": {
        "tag": "DUELLENS RESULTAT", "title": "Snyggt kämpat!", "art": "🎲 ✨ 🏅",
        "text": lambda: (f"Du rullar {state['last_roll']}! " + ("Tusse snubblar på sin egen mössa och utropar dig till hedersmästare. Du får två guldmynt." if state["last_roll"] >= 4 else "Tusse vinner knappt, men ni skrattar och gör en high-five. Du får ändå ett guldmynt.")),
        "effect": "duel", "choices": [("🪨", "Fortsätt till grottan", "cave")]
    },
    "cave": {
        "tag": "KAPITEL 3 · DEN GLÖMDA GROTTAN", "title": "Ett litet pip i mörkret", "art": "🕯️ 🪨 🐲",
        "text": "Grottan glimmar av kristaller. Längst in hör du ett ynkligt pip. Där sitter en pytteliten drake med lila vingar. Bredvid den ligger byns magiska stjärna! Draken ser rädd ut, inte farlig.",
        "choices": [("🗣️", "Fråga draken vad som hänt", "dragon"), ("🍯", "Erbjud draken något gott", "kind"), ("🔮", "Undersök den magiska stjärnan", "star")]
    },
    "dragon": {
        "tag": "ETT LITET FÖRTROENDE", "title": "Draken heter Puff", "art": "🐲 💬 💜",
        "text": "Draken heter Puff. Den tog stjärnan för att den lyste så fint, men nu hittar Puff inte ut ur grottan. Du lovar att hjälpa till. Puff nosar försiktigt på din hand och börjar spinna som en katt.",
        "choices": [("🌟", "Visa Puff vägen hem med stjärnan", "ending")]
    },
    "kind": {
        "tag": "ETT GOTT HJÄRTA", "title": "Delad glädje", "art": "🍯 🐲 ✨",
        "text": "Du delar ditt mellanmål med Puff. Den lilla draken nyser en dusch av gnistrande stjärnstoft! Stjärnan är hel och Puff är redo att följa med dig hem.",
        "effect": "kind", "choices": [("🌟", "Ta med Puff och stjärnan hem", "ending")]
    },
    "star": {
        "tag": "STJÄRNLJUS", "title": "En magisk upptäckt", "art": "🌟 🔮 🌟",
        "text": "Du ser små runor på stjärnans kant. De betyder: ”Det som delas blir aldrig mindre.” Stjärnan lyser starkare när Puff kommer nära. Du förstår att Puff också behöver en trygg plats.",
        "choices": [("🌟", "Följ med Puff hem till byn", "ending")]
    },
    "ending": {
        "tag": "ÄVENTYRET ÄR KLART", "title": "En stjärna för alla", "art": "🏡 🌟 🐲",
        "text": "Ni kommer hem när kvällshimlen blir mörkblå. Byn jublar när stjärnan sätts tillbaka. Puff får bo i det gamla klocktornet, där den kan se alla sina nya vänner.\n\nDu har klarat äventyret! Men sagor tar aldrig riktigt slut…",
        "choices": [("🔁", "Spela äventyret igen", "restart"), ("🎒", "Titta på din ryggsäck", "bag")]
    }
}

def element(id):
    return document.getElementById(id)

def add_item(name):
    if name not in state["items"]:
        state["items"].append(name)

def update_stats():
    hero = state["hero"]
    if not hero:
        return
    element("hp-value").textContent = f'{hero["hp"]} / {hero["hp"]}'
    element("hp-meter").style.width = "100%"
    element("xp-value").textContent = f'{state["xp"]} XP'
    element("coin-value").textContent = str(state["coins"])
    count = len(state["items"])
    element("item-count").textContent = f'{count} ' + ("sak" if count == 1 else "saker")
    inventory = element("inventory")
    inventory.innerHTML = ""
    items = state["items"] or ["Ryggsäcken är tom"]
    for item in items:
        li = document.createElement("li")
        li.textContent = ("✦ " if state["items"] else "") + item
        inventory.appendChild(li)

def apply_effect(scene_id):
    if scene_id in state["seen"]:
        return
    state["seen"].add(scene_id)
    if scene_id == "talk":
        state["coins"] += 2
        state["xp"] += 2
        add_item("Glittrig sten")
    elif scene_id == "feed":
        state["coins"] += 1
        state["xp"] += 3
        state["items"] = [x for x in state["items"] if x not in ("Blåbär", "Blåbärsmuffins")]
        add_item("Tusses vänskapsband")
    elif scene_id == "trick":
        state["coins"] += 1
        state["xp"] += 2
    elif scene_id == "duel":
        state["coins"] += 2 if state["last_roll"] >= 4 else 1
        state["xp"] += 2
    elif scene_id == "kind":
        state["xp"] += 2
        add_item("Stjärnstoft")

def show_scene(scene_id):
    state["scene"] = scene_id
    scene = SCENES[scene_id]
    apply_effect(scene_id)
    element("scene-tag").textContent = scene["tag"]
    element("scene-title").textContent = scene["title"]
    element("scene-art").textContent = scene["art"]
    story = scene["text"]() if callable(scene["text"]) else scene["text"]
    element("story-text").textContent = story
    choices_el = element("choices")
    choices_el.innerHTML = ""
    choices = list(scene["choices"])
    if scene_id == "bridge" and any(x in state["items"] for x in ("Blåbär", "Blåbärsmuffins")):
        choices.insert(0, ("🫐", "Bjud Tusse på blåbär", "feed"))
    if scene_id == "bridge" and "Glittrig fjäder" not in state["items"] and "owl" in state["seen"]:
        add_item("Glittrig fjäder")
    for icon, label, target in choices:
        button = document.createElement("button")
        button.type = "button"
        button.className = "choice-button"
        icon_el = document.createElement("span")
        icon_el.className = "choice-icon"
        icon_el.textContent = icon
        text_el = document.createElement("span")
        text_el.textContent = label
        button.appendChild(icon_el)
        button.appendChild(text_el)
        callback = create_proxy(lambda event, next_scene=target: choose(next_scene))
        callbacks.append(callback)
        button.addEventListener("click", callback)
        choices_el.appendChild(button)
    update_stats()

def choose(target):
    if target == "restart":
        start_over()
    elif target == "berries":
        add_item("Blåbär")
        state["xp"] += 1
        show_scene("berries")
    elif target == "duel":
        state["last_roll"] = random.randint(1, 6)
        show_scene("duel")
    else:
        show_scene(target)

def start_over():
    state.update({"hero": None, "xp": 0, "coins": 0, "items": [], "scene": "start", "last_roll": 1, "seen": set()})
    element("hero-screen").hidden = False
    element("adventure-screen").hidden = True
    element("dice-result").textContent = ""

def pick_hero(event):
    key = event.currentTarget.dataset.hero
    state["hero"] = dict(HJALTAR[key])
    element("hero-screen").hidden = True
    element("adventure-screen").hidden = False
    element("hero-avatar").textContent = state["hero"]["emoji"]
    element("hero-name").textContent = state["hero"]["name"]
    show_scene("start")

def roll_dice(event):
    number = random.randint(1, 6)
    state["last_roll"] = number
    message = "Maximal tärningsmagi!" if number == 6 else ("Tur på din sida!" if number >= 4 else "Nästa gång kanske!")
    element("dice-result").textContent = f"Du slog en {number}! {message}"

for button in document.querySelectorAll("[data-hero]"):
    callback = create_proxy(pick_hero)
    callbacks.append(callback)
    button.addEventListener("click", callback)

for button_id, function in (("restart", start_over), ("roll-dice", roll_dice)):
    callback = create_proxy(function)
    callbacks.append(callback)
    element(button_id).addEventListener("click", callback)
