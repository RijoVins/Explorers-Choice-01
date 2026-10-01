export type Faq = { question: string; answer: string };

export const faqs: Faq[] = [
  {
    question: "How large are your groups?",
    answer:
      "Small enough to feel human. Most packages run with a maximum of 10–14 travellers, plus a dedicated local guide and private driver where needed. Small groups mean better conversation, faster logistics and the freedom to move at your own pace.",
  },
  {
    question: "Do I need to be fit to travel with you?",
    answer:
      "You don't need to be an athlete. Most days involve gentle walking—heritage lanes, ghats, market strolls. A few packages include a slightly longer hike (the Ladakh high passes, the tea trails of Munnar), which our team will flag clearly so you can choose the right trip.",
  },
  {
    question: "What's included in the price?",
    answer:
      "Every package spells out exactly what is included: accommodation, local transport, a dedicated guide, daily breakfast and selected dinners, and every experience listed in the itinerary. International flights are usually separate so you can choose the routing that suits you.",
  },
  {
    question: "How does booking work?",
    answer:
      "Choose a package and hit BOOK NOW. Our travel team will reach out within one working day to confirm dates, answer questions and arrange the remaining details. A small deposit reserves your place; the balance is due closer to departure.",
  },
  {
    question: "Can I customise a package?",
    answer:
      "Every journey is designed to work as it is, but our planners can tailor the edges—extra nights, an early arrival, or a private departure. Reach out and we will shape it around your needs.",
  },
  {
    question: "What happens if I need to change or cancel?",
    answer:
      "Plans change; we know that. Cancellation and change terms are shown on each package page and in our booking conditions. Your travel planner will walk you through the options before you commit.",
  },
  {
    question: "Do you handle visas and travel insurance?",
    answer:
      "Your planner will advise on visa requirements for your nationality and recommend trusted travel-insurance partners. We cannot arrange insurance on your behalf, but we can make sure you know what is needed.",
  },
  {
    question: "Who are your guides?",
    answer:
      "Local people who live in the places we visit. We work with the same guides year after year—they are part of our team, not a subcontracted service. They bring the stories, the side streets and the sense that you are travelling with a friend.",
  },
];

export type Planner = {
  name: string;
  role: string;
  speciality: string;
  image: string;
  quote: string;
};

export const planners: Planner[] = [
  {
    name: "Maya Sharma",
    role: "Head of Destinations",
    speciality: "Rajasthan · Kashmir · Ladakh",
    image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=600&q=80",
    quote: "Travel should leave you with fewer assumptions than you started with.",
  },
  {
    name: "Arjun Verma",
    role: "Senior Travel Planner",
    speciality: "Kerala · Goa · Andaman",
    image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=600&q=80",
    quote: "The best itineraries are the ones that give you room to be surprised.",
  },
  {
    name: "Fatima Noor",
    role: "Travel Planner",
    speciality: "Varanasi · Agra · Himachal",
    image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=600&q=80",
    quote: "A good guide doesn't explain a place. They introduce you to it.",
  },
  {
    name: "Raghav Iyer",
    role: "Operations & Care",
    speciality: "Goa · Kerala · logistics",
    image: "https://images.unsplash.com/photo-1556157388-97ec21184b4a?auto=format&fit=crop&w=600&q=80",
    quote: "The details that feel invisible on the trip are the ones we worked hardest on.",
  },
];
