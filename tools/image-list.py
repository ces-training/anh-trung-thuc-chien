# Sinh tools/image-list.json: danh sách tranh cần Gemini vẽ (chạy: python3 tools/image-list.py)
import json, pathlib
STYLE = ("Photorealistic editorial photograph, natural soft daylight, real adults, warm and friendly mood, "
         "modern Vietnamese urban setting, clean uncluttered composition, subtle accents of cobalt blue, red and sunflower yellow. "
         "Absolutely no text, letters, numbers, logos, signage, captions or watermarks anywhere in the image; any badges, screens, papers or cards are blank. "
         "Natural human anatomy: every person has exactly two arms and two hands with five fingers; avoid extra or floating hands.")
PORTRAIT = "Chest-up portrait, looking at the camera with a natural smile, plain soft blue-grey studio background, 50mm lens. "
CHARS = {
  "char-an": "An, a Vietnamese woman about 26 years old, shoulder-length straight black bob haircut, cobalt blue blouse, yellow lanyard with a blank white badge.",
  "char-tom": "Tom, a British man about 30, short ginger hair, light freckles, green crew-neck sweater, relaxed and cheerful.",
  "char-kevin": "Kevin, an Asian-American man about 32, short dark brown hair, thin black glasses, navy button-up shirt.",
  "char-linh": "Linh, a Vietnamese woman about 24, long straight black hair, mustard yellow top, bright friendly expression.",
  "char-sarah": "Sarah Lee, a Korean-American businesswoman about 38, black bob haircut, charcoal blazer over a white shirt, confident.",
  "char-wangli": "Wang Li, a Chinese woman about 24, black hair in a high ponytail, red knit sweater, cheerful university student.",
  "char-minh": "Minh, a Vietnamese man about 25, short black hair, green casual shirt, friendly.",
  "char-wangjl": "Manager Wang, a Chinese businessman about 50, short greying hair, dark navy suit, red tie, rimless glasses, polite and warm.",
}
SCENES = {
  "scene-en-networking": (["char-an", "char-tom"], "A weekend networking event in a bright Hanoi co-working space with colourful bunting: An (first reference) and Tom (second reference) meet for the first time, shaking hands and smiling, each holding a drink, other guests softly blurred behind."),
  "scene-en-fair": (["char-kevin", "char-linh"], "A busy career fair hall: Kevin (first reference) starts a conversation with Linh (second reference) in front of a blank exhibition booth, both holding blank brochures."),
  "scene-en-office": (["char-an", "char-tom"], "First day at work in a modern open-plan office: Tom (second reference) welcomes An (first reference) at the marketing team desks, An holds a small box of belongings, both smiling."),
  "scene-en-meeting": (["char-an", "char-sarah"], "A formal business meeting room with a city view: An (first reference) and Sarah Lee (second reference) exchange blank business cards across the table, polite and professional."),
  "scene-zh-networking": (["char-an", "char-wangli"], "A Vietnamese–Chinese student exchange event in a university hall decorated with red lanterns: An (first reference) meets Wang Li (second reference), both waving hello and smiling."),
  "scene-zh-classroom": (["char-minh", "char-wangli"], "First day of a small adult language class with a blank whiteboard: Minh (first reference) introduces himself to Wang Li (second reference), both seated at desks turned towards each other."),
  "scene-zh-meeting": (["char-an", "char-wangjl"], "A formal meeting room in a company office: An (first reference) receives a blank business card from Manager Wang (second reference) with both hands, slight respectful bow, tea cups on the table."),
}
CARDS = {
  "wave": "A young Vietnamese professional waving hello to a colleague across a sunny office lobby.",
  "handshake": "Two adult professionals, a Vietnamese woman and a European man, shaking hands warmly at a networking event, close-up on smiles and handshake.",
  "name": "Close-up of a hand holding a blank white name badge on a yellow lanyard, office background softly blurred.",
  "student": "An adult university student in Hanoi with a backpack and books walking on a green campus, smiling.",
  "teacher": "A friendly adult teacher explaining something in front of a blank whiteboard to a small class of adult learners.",
  "work": "Adults working focused at laptops in a modern bright office in Hanoi.",
  "vietnam": "Hoan Kiem Lake in Hanoi in the morning with trees and the red bridge, people exercising, no signs.",
  "china": "Close-up of glowing red Chinese paper lanterns with golden tassels hanging along a traditional old street at dusk, shallow depth of field, a few people softly blurred in the background, plain lanterns without any characters.",
  "engineer": "A Vietnamese engineer wearing a yellow hard hat and safety vest checking a tablet at a construction site.",
  "calc": "An accountant at a tidy desk using a calculator and reviewing blank paper documents, laptop beside her.",
  "sales": "A friendly sales assistant helping a customer choose a product in a bright retail store.",
  "designer": "A graphic designer sketching on a drawing tablet next to colour swatches in a creative studio.",
  "manager": "A manager leading a short stand-up meeting with her team in front of a glass wall with blank sticky notes.",
  "colleague": "Two colleagues chatting and laughing next to a coffee machine in an office kitchen.",
  "team": "A diverse team of five adults having a friendly meeting around a table with laptops.",
  "company": "Exterior of a modern glass office building in Hanoi on a clear day, people entering, no signs.",
  "card": "Close-up of two hands exchanging a blank white business card across a meeting table.",
  "email": "A professional typing an email on a laptop at a café table, screen content not readable.",
  "home": "A peaceful Vietnamese hometown scene: a small house with a garden and rice fields at golden hour.",
  "city": "Hanoi city skyline at sunset with modern buildings and the Red River.",
  "from": "A traveller with a suitcase walking through a bright airport terminal, departures area, no readable signs.",
  "where": "Two adults looking at a paper map together on a city street, pointing and smiling.",
  "uk": "A classic London street with a red double-decker bus and the Elizabeth Tower in the distance, no readable signs.",
  "morning": "An office worker holding a cup of coffee and greeting a colleague cheerfully in the morning sunlight.",
  "new": "A new employee on her first day carrying a small box of belongings into an office, colleagues welcoming her.",
  "repeat": "At a noisy networking event, a woman leans in politely with a hand near her ear to hear her conversation partner.",
  "role": "Close-up of a blank employee ID badge clipped to a blazer pocket.",
  "cart": "A purchasing manager checking stacked cardboard boxes with a tablet in a clean warehouse.",
  "bye": "Two colleagues waving goodbye to each other at an office door at the end of the day.",
  "thanks": "A woman smiling gratefully with a hand on her heart, thanking a colleague who hands her a coffee.",
  "me": "At a networking event, a young Vietnamese woman introduces herself, smiling, one hand placed lightly on her chest, the listener seen from behind slightly blurred.",
  "you": "A friendly man at a meetup gestures politely with an open palm toward the woman he is talking to, inviting her, both smiling.",
  "she": "In an office, a man introduces a female colleague to a visitor, gesturing toward her with an open hand while she smiles and waves.",
  "person": "A row of four diverse adults standing side by side at a community event, each smiling at the camera, simple and clear.",
  "what": "A young adult with a curious, slightly puzzled expression, palms turned up, asking a question to a friend in a café.",
  "question": "In a small adult language class, a learner raises her hand to ask a question while the teacher turns to listen.",
  "is": "Two colleagues talking, one nodding firmly with a confident smile as if saying 'yes, that is right', pointing at a blank document.",
  "also": "Two friends sitting at a café table, each holding an identical cup of coffee, clinking cups lightly and smiling at each other as if saying \"me too\", simple calm pose.",
  "no": "A woman politely shaking her head and raising one hand in a gentle 'no' gesture during a friendly conversation, smiling.",
  "back": "A woman finishes speaking and turns her open palm toward her conversation partner, inviting him to answer, both smiling at a networking event.",
  "polite": "A young professional politely serving tea to an older business guest in a meeting room.",
}

# ---- trang chủ: người hướng dẫn, bản đồ hành trình, thẻ phòng ----
HOME_REF = {
  "coach-khang-hello": (["coach-khang"], "Khang (the man in the reference image) sits at a bright, cosy Hanoi café table with a laptop and a notebook, turns toward the camera and waves hello with a warm, gentle smile. He is placed on the left third of the frame; the right two thirds are softly blurred café space."),
  "coach-vy-hello": (["coach-vy"], "Vy (the woman in the reference image) sits at a bright, cosy Hanoi café table with a laptop and a notebook, turns toward the camera with a playful, witty smile and a small wave. She is placed on the left third of the frame; the right two thirds are softly blurred café space."),
}
HOME = {
  "coach-khang": ("1:1", PORTRAIT + "Khang, a handsome Vietnamese man about 30, neat short black hair, kind eyes, warm gentle smile, light blue oxford shirt under a navy knit cardigan, calm and caring teacher."),
  "coach-vy": ("1:1", PORTRAIT + "Vy, a pretty Vietnamese woman about 27, shoulder-length wavy dark brown hair, bright playful smile with a hint of humour, cream blouse with a mustard cardigan, cheerful teacher."),
  "journey-en": ("16:9", "Wide panoramic photograph of Hanoi at golden hour seen from a high rooftop: West Lake, modern towers and tree-lined streets, soft haze, calm, lots of open sky, no people in focus."),
  "journey-zh": ("16:9", "Wide panoramic photograph of a modern riverside city at dusk with traditional curved Chinese temple roofs in the foreground and glass towers in the distance, warm lights, calm, open sky."),
  "room-howto": ("4:3", "A young Vietnamese woman studying with earphones and a phone at a sunny desk next to a small kitchen timer and a planner, focused and relaxed."),
  "room-achieve": ("4:3", "A young Vietnamese professional smiling with satisfaction at a laptop, a notebook with ticked boxes and a coffee on the desk, sense of accomplishment."),
  "room-rewards": ("4:3", "A neatly wrapped gift box with a red ribbon, a takeaway coffee cup and a blank white ticket on a wooden table, warm morning light."),
  "room-live": ("4:3", "A small group of Vietnamese adults and two foreigners chatting and laughing around a café table at a weekend language meetup, blank name tags."),
  "room-review": ("4:3", "A neat stack of blank index cards with colourful tabs, a phone and a cup of tea on a cosy desk, soft light."),
  "room-career": ("4:3", "A confident young Vietnamese professional shaking hands with two interviewers in a modern office meeting room, a closed certificate folder on the table."),
}
items = []
for k, d in CHARS.items():
    items.append({"key": k, "aspect": "1:1", "refs": [], "prompt": PORTRAIT + d + " " + STYLE})
for k, (refs, d) in SCENES.items():
    items.append({"key": k, "aspect": "16:9", "refs": refs, "prompt": "Use the people shown in the reference images, keeping their faces, hair and clothes consistent. " + d + " Medium-wide shot, both people clearly visible from the waist up. " + STYLE})
for k, (asp, d) in HOME.items():
    items.append({"key": k, "aspect": asp, "refs": [], "prompt": d + " " + STYLE})
for k, (refs, d) in HOME_REF.items():
    items.append({"key": k, "aspect": "16:9", "refs": refs, "prompt": "Use the person shown in the reference image, keeping face, hair and clothes consistent. " + d + " " + STYLE})
for k, d in CARDS.items():
    items.append({"key": k, "aspect": "4:3", "refs": [], "prompt": d + " " + STYLE})
pathlib.Path(__file__).with_name("image-list.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(items), "tranh")
