"""
Multi-Agent Chat Simulation with Speech Recognition
Foundation of AI - Agent Systems Demo
Topics: Agent Communication, Message Passing, Negotiation,
        Trust, NLP, Speech Recognition, Decision Making
"""
import pyttsx3, time

# -- 1. MESSAGE PASSING SYSTEM --
class Message:
    def __init__(self, sender, receiver, msg_type, content, price=0):
        self.sender = sender
        self.receiver = receiver
        self.msg_type = msg_type   # "offer", "counter", "accept", "reject"
        self.content = content
        self.price = price

class MessageBus:
    """Central message passing system between agents"""
    def __init__(self):
        self.log = []
    def send(self, msg):
        self.log.append(msg)
        print(f"  [{msg.sender} -> {msg.receiver}] ({msg.msg_type}) {msg.content}")

# -- 2. BASE AGENT WITH TRUST --
class Agent:
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.trust = 0.5  # trust score 0 to 1

    def update_trust(self, delta):
        self.trust = max(0, min(1, self.trust + delta))

    def send(self, receiver, msg_type, content, price=0):
        msg = Message(self.name, receiver, msg_type, content, price)
        self.bus.send(msg)
        return msg

# -- 3. BUYER AGENT (Decision Making) --
class BuyerAgent(Agent):
    def __init__(self, name, bus, budget=1000, target=500):
        super().__init__(name, bus)
        self.budget = budget
        self.target = target
        self.offer = target * 0.6  # start low (anchoring strategy)

    def respond(self, msg):
        if msg.msg_type in ("offer", "counter"):
            # DECISION TREE: accept, counter, or reject
            if msg.price <= self.target:
                self.update_trust(0.1)
                return self.send(msg.sender, "accept",
                    f"Deal! I accept ${msg.price:.0f}!", msg.price)
            elif msg.price > self.budget:
                self.update_trust(-0.1)
                return self.send(msg.sender, "reject",
                    f"${msg.price:.0f} is over my budget!", msg.price)
            else:
                # Concession: increase offer slowly, trust speeds it up
                gap = msg.price - self.offer
                self.offer += gap * (0.15 + self.trust * 0.05)
                self.offer = min(self.offer, self.budget)
                self.update_trust(0.05)
                return self.send(msg.sender, "counter",
                    f"How about ${self.offer:.0f}?", self.offer)

# -- 4. SELLER AGENT (Utility-Based Decisions) --
class SellerAgent(Agent):
    def __init__(self, name, bus, cost=300, asking=800):
        super().__init__(name, bus)
        self.cost = cost
        self.asking = asking
        self.price = asking
        self.min_price = cost * 1.5  # 50% minimum profit margin
        self.rounds = 0

    def respond(self, msg):
        self.rounds += 1
        if msg.msg_type in ("counter", "offer"):
            # UTILITY FUNCTION: profit * trust factor
            profit = (msg.price - self.cost) / self.cost
            utility = profit * (0.5 + self.trust)

            if msg.price >= self.min_price and utility > 0.5:
                self.update_trust(0.1)
                return self.send(msg.sender, "accept",
                    f"Deal at ${msg.price:.0f}! Pleasure doing business.", msg.price)
            else:
                # Concede gradually
                self.price -= (self.price - msg.price) * 0.15
                self.price = max(self.price, self.min_price)
                self.update_trust(0.03)
                return self.send(msg.sender, "counter",
                    f"I can do ${self.price:.0f}. Quality item!", self.price)

# -- 5. SIMPLE NLP: Sentiment Analysis --
def analyze_sentiment(text):
    positive = {"deal", "accept", "good", "great", "fair", "agree", "pleasure"}
    negative = {"reject", "expensive", "budget", "no", "high", "over"}
    words = set(text.lower().split())
    pos = len(words & positive)
    neg = len(words & negative)
    if pos > neg: return "Positive :)"
    elif neg > pos: return "Negative :("
    return "Neutral :|"

# -- 6. TEXT-TO-SPEECH --
engine = pyttsx3.init()
engine.setProperty('rate', 160)
voices = engine.getProperty('voices')

def speak(text, voice_idx=0):
    if voice_idx < len(voices):
        engine.setProperty('voice', voices[voice_idx].id)
    engine.say(text)
    engine.runAndWait()

# ====================================================
#  MAIN: Run the negotiation simulation
# ====================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  MULTI-AGENT NEGOTIATION DEMO")
    print("  Foundation of AI - Agent Systems")
    print("=" * 50)

    bus = MessageBus()
    seller = SellerAgent("Seller", bus, cost=300, asking=800)
    buyer  = BuyerAgent("Buyer", bus, budget=1000, target=500)

    print(f"\n  Seller cost: $300 | Asking: $800")
    print(f"  Buyer budget: $1000 | Target: $500\n")

    # Seller starts negotiation
    msg = seller.send("Buyer", "offer",
        f"Welcome! Item available for ${seller.asking:.0f}.", seller.asking)
    speak(msg.content, voice_idx=0)

    # Negotiation loop (max 8 rounds)
    for round_num in range(1, 9):
        print(f"\n-- Round {round_num} --")

        # Buyer responds
        msg = buyer.respond(msg)
        print(f"  Sentiment: {analyze_sentiment(msg.content)}")
        print(f"  Trust -> Buyer:{buyer.trust:.2f} | Seller:{seller.trust:.2f}")
        speak(msg.content, voice_idx=min(1, len(voices)-1))
        time.sleep(0.5)

        if msg.msg_type in ("accept", "reject"):
            break

        # Seller responds
        msg = seller.respond(msg)
        print(f"  Sentiment: {analyze_sentiment(msg.content)}")
        speak(msg.content, voice_idx=0)
        time.sleep(0.5)

        if msg.msg_type == "accept":
            break

    # -- Results --
    print("\n" + "=" * 50)
    if msg.msg_type == "accept":
        print(f"  DEAL CLOSED at ${msg.price:.0f}!")
        print(f"  Buyer saved: ${buyer.budget - msg.price:.0f}")
        print(f"  Seller profit: ${msg.price - seller.cost:.0f}")
        speak(f"Deal closed at {msg.price:.0f} dollars!")
    else:
        print("  NO DEAL REACHED")
        speak("No deal was reached.")

    print(f"\n  Total messages: {len(bus.log)}")
    print(f"  Final trust -> Buyer:{buyer.trust:.2f} | Seller:{seller.trust:.2f}")
    print("=" * 50)
