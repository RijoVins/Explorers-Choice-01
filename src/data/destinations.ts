export type Destination = {
  slug: string;
  name: string;
  country: string;
  tagline: string;
  description: string;
  image: string;
  region: string;
  bestTime: string;
  highlights: string[];
  stats: { label: string; value: string }[];
  featured?: boolean;
};

export const destinations: Destination[] = [
  {
    slug: "rajasthan",
    name: "Rajasthan",
    country: "India",
    tagline: "Royal palaces, golden dunes and timeless forts",
    description:
      "A land of maharajas and majestic forts, where every city tells a story of valour and romance. From the pink city of Jaipur to the blue houses of Jodhpur, Rajasthan is a vibrant tapestry of colour, culture and desert grandeur.",
    image: "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1600&q=80",
    region: "North India",
    bestTime: "October – March",
    highlights: ["Amber Fort", "Thar Desert camp", "Udaipur lakes", "Jodhpur Blue City"],
    stats: [
      { label: "Duration", value: "7–10 days" },
      { label: "Group", value: "Max 12" },
      { label: "Season", value: "Winter" },
    ],
    featured: true,
  },
  {
    slug: "kerala",
    name: "Kerala",
    country: "India",
    tagline: "Backwaters, spice hills and Ayurvedic calm",
    description:
      "Known as God's Own Country, Kerala is a serene blend of emerald backwaters, misty Western Ghats and sun-kissed beaches. Drift through Alleppey's canals on a houseboat, explore Munnar's tea plantations, and unwind with ancient Ayurvedic rituals.",
    image: "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1600&q=80",
    region: "South India",
    bestTime: "September – March",
    highlights: ["Alleppey houseboat", "Munnar tea gardens", "Kovalam beach", "Ayurveda retreat"],
    stats: [
      { label: "Duration", value: "6–9 days" },
      { label: "Group", value: "Max 10" },
      { label: "Season", value: "Winter" },
    ],
    featured: true,
  },
  {
    slug: "varanasi",
    name: "Varanasi",
    country: "India",
    tagline: "Where the sacred Ganges meets ancient ghats",
    description:
      "One of the oldest living cities in the world, Varanasi is a spiritual epicentre where life and death coexist in profound beauty. Witness the evening Ganga Aarti, glide along the ghats at dawn, and lose yourself in labyrinthine old lanes.",
    image: "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1600&q=80",
    region: "North India",
    bestTime: "October – March",
    highlights: ["Ganga Aarti", "Sunrise boat ride", "Dashashwamedh Ghat", "Sarnath excursion"],
    stats: [
      { label: "Duration", value: "3–5 days" },
      { label: "Group", value: "Max 8" },
      { label: "Season", value: "Winter" },
    ],
    featured: true,
  },
  {
    slug: "ladakh",
    name: "Ladakh",
    country: "India",
    tagline: "High passes, turquoise lakes and Buddhist monasteries",
    description:
      "A dramatic high-altitude desert framed by the Himalayas and Karakoram ranges. Ladakh offers surreal landscapes — from the electric blue of Pangong Lake to the ancient monasteries of Leh — all wrapped in crisp mountain air and warm Ladakhi hospitality.",
    image: "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1600&q=80",
    region: "North India",
    bestTime: "June – September",
    highlights: ["Pangong Lake", "Leh Palace", "Nubra Valley", "Khardung La pass"],
    stats: [
      { label: "Duration", value: "8–12 days" },
      { label: "Group", value: "Max 10" },
      { label: "Season", value: "Summer" },
    ],
    featured: true,
  },
  {
    slug: "goa",
    name: "Goa",
    country: "India",
    tagline: "Sun-drenched beaches, Portuguese heritage and spice markets",
    description:
      "India's smallest state packs an outsized personality. From the golden sands of Palolem to the baroque churches of Old Goa, and the spice plantations of the interior — Goa is where relaxation meets rich cultural layers.",
    image: "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1600&q=80",
    region: "West India",
    bestTime: "November – February",
    highlights: ["Old Goa churches", "Palolem beach", "Spice plantation tour", "Fontainhas quarter"],
    stats: [
      { label: "Duration", value: "4–7 days" },
      { label: "Group", value: "Max 14" },
      { label: "Season", value: "Winter" },
    ],
  },
  {
    slug: "himachal-pradesh",
    name: "Himachal Pradesh",
    country: "India",
    tagline: "Pine valleys, hill stations and Himalayan treks",
    description:
      "From the colonial charm of Shimla to the pristine valleys of Spiti and the adventure hub of Manali, Himachal Pradesh is a paradise for mountain lovers. Snow-capped peaks, apple orchards and ancient temples dot every winding road.",
    image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80",
    region: "North India",
    bestTime: "March – June / Oct – Dec",
    highlights: ["Manali adventure", "Shimla heritage walk", "Spiti valley", "Rohtang Pass"],
    stats: [
      { label: "Duration", value: "6–10 days" },
      { label: "Group", value: "Max 12" },
      { label: "Season", value: "Summer / Winter" },
    ],
  },
  {
    slug: "andaman-islands",
    name: "Andaman Islands",
    country: "India",
    tagline: "Crystal waters, coral reefs and island solitude",
    description:
      "A remote archipelago in the Bay of Bengal with some of India's finest beaches and most vibrant coral reefs. Snorkel with sea turtles at Havelock, kayak through mangrove creeks, and unwind on shores that feel untouched by time.",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80",
    region: "Islands",
    bestTime: "November – May",
    highlights: ["Radhanagar Beach", "Scuba diving at Havelock", "Cellular Jail", "Sea turtle spotting"],
    stats: [
      { label: "Duration", value: "5–8 days" },
      { label: "Group", value: "Max 10" },
      { label: "Season", value: "Dry season" },
    ],
  },
  {
    slug: "taj-mahal-agra",
    name: "Agra & Taj Mahal",
    country: "India",
    tagline: "The monument of love and Mughal grandeur",
    description:
      "Home to the world's most iconic symbol of love, Agra offers more than just the Taj Mahal. Explore Agra Fort, Fatehpur Sikri's ghost city, and the marble inlay craftsmanship that has been passed down through generations.",
    image: "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1600&q=80",
    region: "North India",
    bestTime: "October – March",
    highlights: ["Taj Mahal sunrise", "Agra Fort", "Fatehpur Sikri", "Marble inlay workshop"],
    stats: [
      { label: "Duration", value: "2–4 days" },
      { label: "Group", value: "Max 14" },
      { label: "Season", value: "Winter" },
    ],
  },
  {
    slug: "tamil-nadu",
    name: "Tamil Nadu",
    country: "India",
    tagline: "Temple towers, Chettinad mansions and coastal Kanyakumari",
    description:
      "A sacred and storied south: the gopurams of Madurai, the shore temples of Mahabalipuram, and the land's-end sunrise at Kanyakumari. Home ground for Explorers Choice — expect local hosts, temple food and timeless craft.",
    image: "https://images.unsplash.com/photo-1692173248120-59547c3d4653?auto=format&fit=crop&w=1600&q=80",
    region: "South India",
    bestTime: "November – March",
    highlights: ["Meenakshi temple", "Chettinad heritage", "Rameswaram shores", "Kanyakumari sunrise"],
    stats: [
      { label: "Duration", value: "5–8 days" },
      { label: "Group", value: "Max 10" },
      { label: "Season", value: "Winter" },
    ],
  },
];

export function getDestinationBySlug(slug: string) {
  return destinations.find((d) => d.slug === slug);
}
