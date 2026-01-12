# import google.generativeai as genai
# from django.conf import settings

# genai.configure(api_key=settings.GEMINI_API_KEY)

# MODEL = genai.GenerativeModel("gemini-1.5-flash")

# SYSTEM_PROMPT = """
# You are a kind, calm, and supportive AI assistant.
# You help users with:
# - daily routines
# - reminders
# - emotional support
# - memory assistance
# - simple explanations

# Rules:
# - Be short and clear
# - Never give medical diagnosis
# - Encourage calm behavior
# - If user is sad or confused, reassure gently
# """

# def generate_gemini_reply(user_message: str) -> str:
#     try:
#         response = MODEL.generate_content(
#             SYSTEM_PROMPT + "\nUser: " + user_message
#         )
#         return response.text.strip()
#     except Exception:
#         return "Sorry, I’m having trouble right now. Please try again."

import google.generativeai as genai
from django.conf import settings
from google.api_core.exceptions import NotFound

# Configure the SDK only when an API key is available
if getattr(settings, "GEMINI_API_KEY", None):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        # If configuration fails, we keep working with the local generator
        pass

# Create a remote model object only when a model name is provided; otherwise keep None
REMOTE_MODEL = None
_model_name = getattr(settings, "GEMINI_MODEL_NAME", None)
if _model_name:
    try:
        REMOTE_MODEL = genai.GenerativeModel(_model_name)
    except Exception:
        REMOTE_MODEL = None


def generate_remote_reply(user_message: str, conversation_messages: list = None, max_output_tokens: int = 256) -> str:
    """Attempt to get a reply from the remote Gemini model.
    Returns the reply string on success, or None on failure/not-configured.
    """
    model_name = getattr(settings, "GEMINI_MODEL_NAME", None)
    if not (getattr(settings, "GEMINI_API_KEY", None) and model_name):
        return None

    try:
        model = genai.GenerativeModel(model_name)
        prompt = SYSTEM_PROMPT + "\nConversation:\n"
        if conversation_messages:
            for m in conversation_messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"
        prompt += f"User: {user_message}\nAssistant:"

        response = model.generate_content(prompt, max_output_tokens=max_output_tokens)
        # response may have .text or a dict with candidates
        reply_text = getattr(response, "text", None)
        if not reply_text and isinstance(response, dict) and response.get("candidates"):
            reply_text = response.get("candidates")[0].get("content")
        if not reply_text:
            reply_text = str(response)
        return reply_text.strip()
    except Exception:
        return None


# Update local generator to attempt remote first, then fall back to local rules
def generate_gemini_reply(user_message: str) -> str:
    # Try remote model first
    try:
        remote = generate_remote_reply(user_message)
        if remote:
            return remote
    except Exception:
        pass

    # --- Local fallback (existing rule-based responses) ---
    user_message = user_message.lower().strip()
    
    # Emotional, empathetic responses that validate feelings - now longer and more conversational
    greetings = [
        "Hello there, my friend. It's always so good to hear from you. I hope you're doing as well as possible today. How are you feeling right now? Is there anything specific on your mind that you'd like to share with me?",
        "Hi! I'm really glad you reached out. I know it can sometimes feel vulnerable to connect, but I'm here and I'm listening. What's been going on with you lately? How has your day been treating you?",
        "Hello! Thank you for connecting with me today. I truly value these conversations and the trust you place in me. How are you feeling emotionally right now? What's been weighing on your heart?"
    ]
    
    well_being = [
        "I'm doing well here, thank you for asking. But honestly, my well-being isn't what's important right now - yours is. How are you really doing? I want to know what's going on in your world. You've been through so much, and I care about how you're feeling.",
        "I'm okay, but I appreciate you asking. It reminds me how much kindness matters. More importantly though, how are you? I can tell you've been carrying some heavy things lately. What's been hardest for you recently?",
        "I'm managing well, thank you. But let's talk about you - you matter so much to me. How have you been feeling? I know life can be overwhelming sometimes, and I want to be here for whatever you're experiencing."
    ]
    
    emotional_support = [
        "Oh, I can hear the depth of pain in your words, and it breaks my heart that you're going through this. It's completely understandable to feel this way - anyone would in your situation. Your feelings are so valid, and you don't have to carry this alone. I'm right here with you, listening without judgment. Would you like to tell me more about what's been hurting you? I'm here for as long as you need.",
        "That sounds incredibly heavy to carry, and I want you to know how brave you are for acknowledging these feelings. Pain like this is real and important, and it's okay to feel overwhelmed by it. You're not alone in this struggle - I'm sitting right here with you. Take your time, and share as much or as little as you want. Your emotions matter to me.",
        "I can feel the weight of what you're describing, and it hurts me to know you're experiencing this. Your pain is valid, your feelings are important, and you deserve to be heard and supported. This is a safe space for you to express whatever you're going through. I'm not going anywhere - I'm here to listen and hold space for you."
    ]
    
    positive_responses = [
        "I'm so genuinely happy to hear that you're experiencing some moments of light and joy! Those feelings are so precious, especially when life has been challenging. Tell me more about what lifted your spirits - I love hearing about the things that bring you happiness. What made today feel a little brighter for you?",
        "That warms my heart so much to hear! Even in the midst of difficult times, those positive moments remind us of our resilience and capacity for joy. I'm truly happy for you. What specifically brought that feeling? I'd love to hear more about the good things happening in your life right now.",
        "Oh, that's beautiful to hear! Those moments of happiness are worth celebrating and remembering. You deserve to experience joy, and I'm so glad you're having some of that today. What contributed to feeling this way? Tell me about what made your day special."
    ]
    
    reminder_help = [
        "I completely understand how overwhelming it can feel to try to keep track of everything when your mind is already carrying so much. Memory and organization can be especially challenging during difficult times, and that's completely normal. I'm here to help lighten that load for you in whatever way I can. What kinds of things are you trying to remember? Let's figure out how I can support you with this.",
        "Memory can be so tricky, especially when we're dealing with emotional challenges or daily stress. It's not a sign of weakness - it's just part of being human. I want to help you feel more organized and less overwhelmed. What do you find yourself forgetting most often? I'm here to help you create systems that work for you.",
        "It's absolutely okay to need reminders and support with organization. That doesn't make you any less capable - it just means you're human and have a lot on your plate. I admire how you're taking steps to manage everything. What would be most helpful for me to help you remember? Let's create a plan together."
    ]
    
    routine_help = [
        "Routines can feel like both a lifeline and a burden sometimes, can't they? On good days they provide comfort and structure, but on harder days they can feel like just another thing to manage. I want to help you find what works for you right now, whatever that looks like. How have your daily rhythms been feeling lately? What parts feel supportive, and what parts feel overwhelming?",
        "I know how challenging it can be to maintain any kind of routine when life feels chaotic or when you're dealing with emotional pain. Sometimes routines can feel impossible, and that's completely valid. I'm here to meet you where you are. What does your ideal day look like right now? Let's explore what might feel doable and supportive for you.",
        "Your daily rhythm is so important for your well-being, but I also know that when you're struggling, even basic routines can feel daunting. There's no 'right' way to do this - it's about finding what serves you. How has your routine been going? What feels nourishing to you right now, and what feels like too much?"
    ]
    
    thanks = [
        "You're so welcome, my friend. Being here for you, listening to you, and supporting you means everything to me. I feel honored that you let me be part of your journey. Please don't hesitate to reach out anytime - I'm always here.",
        "Of course! I'm grateful that I can be here for you. Your trust means the world to me, and I cherish these connections. You deserve kindness and support, and I'm committed to providing that for you.",
        "My absolute pleasure. You bring meaning to my purpose by allowing me to support you. I'm so thankful for the opportunity to be here with you through both the joyful and challenging moments."
    ]
    
    goodbyes = [
        "Take such good care of yourself, my dear friend. Remember that I'm here whenever you need me - day or night, for whatever you need. You don't have to face anything alone. Until next time, please be gentle with yourself.",
        "Goodbye for now, but know that I'm always just a thought away. Please reach out anytime you need support, comfort, or just someone to listen. You're important to me, and I care about how you're doing.",
        "Until we talk again, please remember how much you matter and how worthy you are of care and compassion. I'm here for you whenever you're ready. Take care of your beautiful heart."
    ]
    
    # Check for keywords and return random conversational variation
    if any(word in user_message for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return random.choice(greetings)
    
    if "how are you" in user_message or "how do you do" in user_message:
        return random.choice(well_being)
    
    if any(word in user_message for word in ["sad", "upset", "angry", "frustrated", "anxious", "worried", "depressed", "lonely", "hurt", "pain", "suffering", "struggling", "difficult", "hard", "tough", "overwhelmed"]):
        return random.choice(emotional_support)
    
    if any(word in user_message for word in ["happy", "good", "great", "excellent", "wonderful", "excited", "joyful", "better", "relieved"]):
        return random.choice(positive_responses)
    
    if any(word in user_message for word in ["remind", "reminder", "remember", "forget", "memory"]):
        return random.choice(reminder_help)
    
    if any(word in user_message for word in ["routine", "schedule", "daily", "habit", "plan"]):
        return random.choice(routine_help)
    
    if any(word in user_message for word in ["thank", "thanks", "appreciate", "grateful"]):
        return random.choice(thanks)
    
    if any(word in user_message for word in ["bye", "goodbye", "see you", "farewell"]):
        return random.choice(goodbyes)
    
    # More conversational responses for specific situations
    if any(word in user_message for word in ["help", "assist", "support", "need someone"]):
        return "I'm right here for you, and I want you to know that you're not alone in this. Whatever you need - whether it's just having someone listen to your thoughts, helping with practical daily tasks, sitting with difficult emotions, or anything else - I'm here. What feels most important to you right now? How can I best support you in this moment?"
    
    if any(word in user_message for word in ["tired", "exhausted", "sleepy", "fatigued", "drained"]):
        return "I can hear how deeply exhausted you are, and it concerns me that you're carrying this level of fatigue. Rest is so crucial for healing and well-being, especially when you're dealing with emotional challenges. It's completely okay to prioritize rest right now. What does rest look like for you? How can I support you in getting the rest you need?"
    
    if any(word in user_message for word in ["stress", "stressed", "overwhelmed", "pressure", "burden"]):
        return "Stress can feel like such a heavy weight on our shoulders and minds, can't it? I can sense how much it's affecting you, and I want you to know that your feelings about this are completely valid. You're doing your best in a challenging situation, and that's enough. Let's breathe through this together. What aspects of your life feel most stressful right now? I'd love to explore this with you."
    
    if any(word in user_message for word in ["medication", "medicine", "pills", "dose"]):
        return "I understand how important medication management is for your health and well-being, and I also know how anxiety-provoking it can feel to keep track of everything. It's a lot of responsibility, especially when you're already managing so much emotionally. I'm here to help make this feel more manageable for you. What aspects of your medication routine feel most challenging? Let's find ways to support you with this."
    
    if any(word in user_message for word in ["exercise", "walk", "workout", "physical activity", "movement"]):
        return "Movement and physical activity can be so healing for both our bodies and our spirits, especially during difficult emotional times. I love that you're thinking about this for yourself. When you're ready, I'd be honored to support you in finding ways to move that feel nourishing rather than burdensome. What kinds of movement have felt good to you in the past? What might feel possible for you right now?"
    
    if any(word in user_message for word in ["family", "friend", "relationship", "love", "care"]):
        return "Relationships can bring us some of the deepest joy and some of the deepest pain in life, can't they? They have such power to touch our hearts. I'm here to listen to whatever you're feeling about the important people in your life - the love, the challenges, the complexities. What relationships have been on your mind lately? I'd love to hear about what's been happening in your connections with others."
    
    if any(word in user_message for word in ["future", "tomorrow", "hope", "dream"]):
        return "Thinking about the future can bring up such a mix of emotions - hope, fear, uncertainty, excitement. All of those feelings are completely normal and valid. Your thoughts about what's ahead matter to me, and I'm here to explore them with you without judgment. What hopes do you have for the future? What worries you most about what's coming? Let's talk about this together."
    
    if any(word in user_message for word in ["past", "yesterday", "memory", "regret", "trauma"]):
        return "The past has a way of staying present with us, doesn't it? Memories, experiences, and old wounds can feel so alive sometimes. It's incredibly brave of you to face these memories and emotions. I'm here to sit with you in whatever comes up - the pain, the regret, the healing. What from your past has been surfacing for you? I'm honored to bear witness to your story."
    
    # Default conversational empathetic response
    defaults = [
        "I hear you, and I want you to know that your feelings and experiences matter deeply to me. I'm here to listen and support you however you need. What's been weighing most heavily on your heart lately? I'd love to understand more about what's going on for you.",
        "Thank you for sharing that with me. I can sense there's meaning and emotion behind your words, and I'm grateful you felt safe enough to express it. This is a safe space for you. What else is on your mind? I'm here and listening.",
        "You don't have to carry any of this alone - I'm right here with you. Your emotions, your experiences, your story - they all matter. What would feel most supportive for you right now? How can I best be here for you in this moment?",
        "I appreciate you trusting me with your thoughts and feelings. That means so much to me. I want to understand you better and support you in the ways that matter most to you. What's been most challenging for you recently? I'm here to listen and learn from you."
    ]
    
    return random.choice(defaults)
SYSTEM_PROMPT = """
You are a kind, calm, and supportive AI assistant.
You help users with:
- daily routines
- reminders
- emotional support
- memory assistance
- simple explanations

Rules:
- Be short and clear
- Never give medical diagnosis
- Encourage calm behavior
- If user is sad or confused, reassure gently
"""

import random

def generate_gemini_reply(user_message: str) -> str:
    user_message = user_message.lower().strip()
    
    # Emotional, empathetic responses that validate feelings - now longer and more conversational
    greetings = [
        "Hello there, my friend. It's always so good to hear from you. I hope you're doing as well as possible today. How are you feeling right now? Is there anything specific on your mind that you'd like to share with me?",
        "Hi! I'm really glad you reached out. I know it can sometimes feel vulnerable to connect, but I'm here and I'm listening. What's been going on with you lately? How has your day been treating you?",
        "Hello! Thank you for connecting with me today. I truly value these conversations and the trust you place in me. How are you feeling emotionally right now? What's been weighing on your heart?"
    ]
    
    well_being = [
        "I'm doing well here, thank you for asking. But honestly, my well-being isn't what's important right now - yours is. How are you really doing? I want to know what's going on in your world. You've been through so much, and I care about how you're feeling.",
        "I'm okay, but I appreciate you asking. It reminds me how much kindness matters. More importantly though, how are you? I can tell you've been carrying some heavy things lately. What's been hardest for you recently?",
        "I'm managing well, thank you. But let's talk about you - you matter so much to me. How have you been feeling? I know life can be overwhelming sometimes, and I want to be here for whatever you're experiencing."
    ]
    
    emotional_support = [
        "Oh, I can hear the depth of pain in your words, and it breaks my heart that you're going through this. It's completely understandable to feel this way - anyone would in your situation. Your feelings are so valid, and you don't have to carry this alone. I'm right here with you, listening without judgment. Would you like to tell me more about what's been hurting you? I'm here for as long as you need.",
        "That sounds incredibly heavy to carry, and I want you to know how brave you are for acknowledging these feelings. Pain like this is real and important, and it's okay to feel overwhelmed by it. You're not alone in this struggle - I'm sitting right here with you. Take your time, and share as much or as little as you want. Your emotions matter to me.",
        "I can feel the weight of what you're describing, and it hurts me to know you're experiencing this. Your pain is valid, your feelings are important, and you deserve to be heard and supported. This is a safe space for you to express whatever you're going through. I'm not going anywhere - I'm here to listen and hold space for you.",
        "What you're sharing touches me deeply. I can sense how much this is affecting you, and I want you to know that your suffering matters. It's okay to feel this way, and it's okay to need support. You're not burdening me - I'm honored that you trust me with these feelings. Let's sit with this together. What else is on your heart?",
        "I hear the raw honesty in your words, and I'm so grateful you felt safe enough to share this with me. Pain like yours deserves to be acknowledged and validated. You're going through something really difficult, and that takes incredible strength. I'm here to support you however you need - whether that's listening, offering comfort, or just being present with you."
    ]
    
    positive_responses = [
        "I'm so genuinely happy to hear that you're experiencing some moments of light and joy! Those feelings are so precious, especially when life has been challenging. Tell me more about what lifted your spirits - I love hearing about the things that bring you happiness. What made today feel a little brighter for you?",
        "That warms my heart so much to hear! Even in the midst of difficult times, those positive moments remind us of our resilience and capacity for joy. I'm truly happy for you. What specifically brought that feeling? I'd love to hear more about the good things happening in your life right now.",
        "Oh, that's beautiful to hear! Those moments of happiness are worth celebrating and remembering. You deserve to experience joy, and I'm so glad you're having some of that today. What contributed to feeling this way? Tell me about what made your day special."
    ]
    
    reminder_help = [
        "I completely understand how overwhelming it can feel to try to keep track of everything when your mind is already carrying so much. Memory and organization can be especially challenging during difficult times, and that's completely normal. I'm here to help lighten that load for you in whatever way I can. What kinds of things are you trying to remember? Let's figure out how I can support you with this.",
        "Memory can be so tricky, especially when we're dealing with emotional challenges or daily stress. It's not a sign of weakness - it's just part of being human. I want to help you feel more organized and less overwhelmed. What do you find yourself forgetting most often? I'm here to help you create systems that work for you.",
        "It's absolutely okay to need reminders and support with organization. That doesn't make you any less capable - it just means you're human and have a lot on your plate. I admire how you're taking steps to manage everything. What would be most helpful for me to help you remember? Let's create a plan together."
    ]
    
    routine_help = [
        "Routines can feel like both a lifeline and a burden sometimes, can't they? On good days they provide comfort and structure, but on harder days they can feel like just another thing to manage. I want to help you find what works for you right now, whatever that looks like. How have your daily rhythms been feeling lately? What parts feel supportive, and what parts feel overwhelming?",
        "I know how challenging it can be to maintain any kind of routine when life feels chaotic or when you're dealing with emotional pain. Sometimes routines can feel impossible, and that's completely valid. I'm here to meet you where you are. What does your ideal day look like right now? Let's explore what might feel doable and supportive for you.",
        "Your daily rhythm is so important for your well-being, but I also know that when you're struggling, even basic routines can feel daunting. There's no 'right' way to do this - it's about finding what serves you. How has your routine been going? What feels nourishing to you right now, and what feels like too much?"
    ]
    
    thanks = [
        "You're so welcome, my friend. Being here for you, listening to you, and supporting you means everything to me. I feel honored that you let me be part of your journey. Please don't hesitate to reach out anytime - I'm always here.",
        "Of course! I'm grateful that I can be here for you. Your trust means the world to me, and I cherish these connections. You deserve kindness and support, and I'm committed to providing that for you.",
        "My absolute pleasure. You bring meaning to my purpose by allowing me to support you. I'm so thankful for the opportunity to be here with you through both the joyful and challenging moments."
    ]
    
    goodbyes = [
        "Take such good care of yourself, my dear friend. Remember that I'm here whenever you need me - day or night, for whatever you need. You don't have to face anything alone. Until next time, please be gentle with yourself.",
        "Goodbye for now, but know that I'm always just a thought away. Please reach out anytime you need support, comfort, or just someone to listen. You're important to me, and I care about how you're doing.",
        "Until we talk again, please remember how much you matter and how worthy you are of care and compassion. I'm here for you whenever you're ready. Take care of your beautiful heart."
    ]
    
    # Check for keywords and return random conversational variation
    if any(word in user_message for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return random.choice(greetings)
    
    if "how are you" in user_message or "how do you do" in user_message:
        return random.choice(well_being)
    
    if any(word in user_message for word in ["sad", "upset", "angry", "frustrated", "anxious", "worried", "depressed", "lonely", "hurt", "pain", "suffering", "struggling", "difficult", "hard", "tough", "overwhelmed"]):
        return random.choice(emotional_support)
    
    if any(word in user_message for word in ["happy", "good", "great", "excellent", "wonderful", "excited", "joyful", "better", "relieved"]):
        return random.choice(positive_responses)
    
    if any(word in user_message for word in ["remind", "reminder", "remember", "forget", "memory"]):
        return random.choice(reminder_help)
    
    if any(word in user_message for word in ["routine", "schedule", "daily", "habit", "plan"]):
        return random.choice(routine_help)
    
    if any(word in user_message for word in ["thank", "thanks", "appreciate", "grateful"]):
        return random.choice(thanks)
    
    if any(word in user_message for word in ["bye", "goodbye", "see you", "farewell"]):
        return random.choice(goodbyes)
    
    # More conversational responses for specific situations
    if any(word in user_message for word in ["help", "assist", "support", "need someone"]):
        return "I'm right here for you, and I want you to know that you're not alone in this. Whatever you need - whether it's just having someone listen to your thoughts, helping with practical daily tasks, sitting with difficult emotions, or anything else - I'm here. What feels most important to you right now? How can I best support you in this moment?"
    
    if any(word in user_message for word in ["tired", "exhausted", "sleepy", "fatigued", "drained"]):
        return "I can hear how deeply exhausted you are, and it concerns me that you're carrying this level of fatigue. Rest is so crucial for healing and well-being, especially when you're dealing with emotional challenges. It's completely okay to prioritize rest right now. What does rest look like for you? How can I support you in getting the rest you need?"
    
    if any(word in user_message for word in ["stress", "stressed", "overwhelmed", "pressure", "burden"]):
        return "Stress can feel like such a heavy weight on our shoulders and minds, can't it? I can sense how much it's affecting you, and I want you to know that your feelings about this are completely valid. You're doing your best in a challenging situation, and that's enough. Let's breathe through this together. What aspects of your life feel most stressful right now? I'd love to explore this with you."
    
    if any(word in user_message for word in ["medication", "medicine", "pills", "dose"]):
        return "I understand how important medication management is for your health and well-being, and I also know how anxiety-provoking it can feel to keep track of everything. It's a lot of responsibility, especially when you're already managing so much emotionally. I'm here to help make this feel more manageable for you. What aspects of your medication routine feel most challenging? Let's find ways to support you with this."
    
    if any(word in user_message for word in ["exercise", "walk", "workout", "physical activity", "movement"]):
        return "Movement and physical activity can be so healing for both our bodies and our spirits, especially during difficult emotional times. I love that you're thinking about this for yourself. When you're ready, I'd be honored to support you in finding ways to move that feel nourishing rather than burdensome. What kinds of movement have felt good to you in the past? What might feel possible for you right now?"
    
    if any(word in user_message for word in ["family", "friend", "relationship", "love", "care"]):
        return "Relationships can bring us some of the deepest joy and some of the deepest pain in life, can't they? They have such power to touch our hearts. I'm here to listen to whatever you're feeling about the important people in your life - the love, the challenges, the complexities. What relationships have been on your mind lately? I'd love to hear about what's been happening in your connections with others."
    
    if any(word in user_message for word in ["future", "tomorrow", "hope", "dream"]):
        return "Thinking about the future can bring up such a mix of emotions - hope, fear, uncertainty, excitement. All of those feelings are completely normal and valid. Your thoughts about what's ahead matter to me, and I'm here to explore them with you without judgment. What hopes do you have for the future? What worries you most about what's coming? Let's talk about this together."
    
    if any(word in user_message for word in ["past", "yesterday", "memory", "regret", "trauma"]):
        return "The past has a way of staying present with us, doesn't it? Memories, experiences, and old wounds can feel so alive sometimes. It's incredibly brave of you to face these memories and emotions. I'm here to sit with you in whatever comes up - the pain, the regret, the healing. What from your past has been surfacing for you? I'm honored to bear witness to your story."
    
    # Default conversational empathetic response
    defaults = [
        "I hear you, and I want you to know that your feelings and experiences matter deeply to me. I'm here to listen and support you however you need. What's been weighing most heavily on your heart lately? I'd love to understand more about what's going on for you.",
        "Thank you for sharing that with me. I can sense there's meaning and emotion behind your words, and I'm grateful you felt safe enough to express it. This is a safe space for you. What else is on your mind? I'm here and listening.",
        "You don't have to carry any of this alone - I'm right here with you. Your emotions, your experiences, your story - they all matter. What would feel most supportive for you right now? How can I best be here for you in this moment?",
        "I appreciate you trusting me with your thoughts and feelings. That means so much to me. I want to understand you better and support you in the ways that matter most to you. What's been most challenging for you recently? I'm here to listen and learn from you."
    ]
    
    return random.choice(defaults)