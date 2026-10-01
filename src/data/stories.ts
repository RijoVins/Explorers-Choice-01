export type Story = {
  slug: string;
  title: string;
  excerpt: string;
  quote: string;
  author: string;
  trip: string;
  date: string;
  image: string;
  body: string[];
};

export const stories: Story[] = [
  {
    slug: "royal-welcome-in-rajasthan",
    title: "A royal welcome in Rajasthan",
    excerpt: "After years of dreaming about India, Arjun and Meera finally walked into a palace in Jaipur—and never wanted to leave.",
    quote: "Every corner felt like it had its own story. We only scratched the surface.",
    author: "Arjun & Meera",
    trip: "Royal Rajasthan",
    date: "December 2024",
    image: "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1400&q=80",
    body: [
      "We had been reading about Rajasthan for years. Work, family, city chaos—there was always a reason to postpone. When we finally called Explorers Choice, we didn't want a rushed checklist of forts. We wanted to feel the romance of the desert.",
      "They understood that straight away. Our journey had everything we had dreamed about—Amber Fort at sunrise, camel safaris into the Thar, a boat ride on Lake Pichola—but also the spaces between. A rooftop chai in Jodhpur's blue lanes. An evening of folk music around a desert campfire. Time to simply sit and soak it all in.",
      "The best part was never having to think about the logistics. Our guide Ravi knew the quietest time for every palace and the best halwa shop in every city. We came home with hundreds of photos, but the memories we talk about most are the small ones.",
    ],
  },
  {
    slug: "stilling-the-mind-in-kerala",
    title: "Finding stillness on the Kerala backwaters",
    excerpt: "A week drifting through Kerala taught Sarah that the best travel moments are often the quietest ones.",
    quote: "We went looking for greenery and found peace. That is the Kerala I will remember.",
    author: "Sarah Thompson",
    trip: "Kerala Backwater Escape",
    date: "February 2025",
    image: "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1400&q=80",
    body: [
      "The plan was rest. I had pictured the houseboat, the tea gardens, the long lazy mornings on the water. I hadn't pictured sitting on my own private deck at dawn, watching a fisherman cast his nets into mirror-still water while kingfishers flickered past.",
      "Our captain, Sunil, seemed to know everyone along the canal. The family selling freshly fried banana chips, the temple priest who waved as we passed, the toddy-shop owner who insisted we taste his coconut milk straight from the shell. Kerala unfolded through hospitality, not monuments.",
      "The Munnar trek was beautiful, of course, with its rolling tea estates. But the moment I carry home is waking on the water with absolutely nothing to do. Then, slowly, the sun warming my face.",
    ],
  },
  {
    slug: "why-varanasi-taught-us-to-slow-down",
    title: "Why Varanasi made us slow down",
    excerpt: "The ghats are famous for their ceremony. Less talked about is what happens when you sit still and just watch.",
    quote: "The itinerary gave us a direction, not a deadline. That made all the difference.",
    author: "Emily & Tom",
    trip: "Spiritual Varanasi",
    date: "November 2024",
    image: "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1400&q=80",
    body: [
      "Before Varanasi, our holidays had a familiar rhythm: wake up early, tick off the thing, rush to the next thing. We thought we were seasoned travellers. We were actually just efficient.",
      "Explorers Choice had planned a day with no fixed plans. Just a quiet ghat, a boatman who knew where the turtles gathered, and a note that said 'ask your host where their grandmother prays'. It became our favourite day of the trip.",
      "We still watched the Ganga Aarti with goosebumps and drifted past the burning ghats in awe. But we also learned that the best itinerary is one that leaves a little white space—especially in a city that has been breathing for five thousand years.",
    ],
  },
  {
    slug: "a-table-for-twelve-in-the-himalayas",
    title: "A table for twelve in the Himalayas",
    excerpt: "The meal we almost skipped became the one none of us wanted to leave.",
    quote: "You can read about a place for years. Then someone opens their home, and suddenly you understand it.",
    author: "The Sharma family",
    trip: "Himachal Mountain Trail",
    date: "June 2025",
    image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1400&q=80",
    body: [
      "We were meant to visit another lookout point that afternoon. Instead, our guide Raju asked if we would like to meet his aunt in a village above Manali. There were twelve of us around a long wooden table by the time lunch was served.",
      "We helped roll the parathas, learned about the family's apple orchards, and watched our children chase butterflies with the neighbour kids while the elders swapped stories in a mix of Hindi, English and laughter.",
      "The snow line at Rohtang Pass was spectacular. But it was that table we talked about on the flight home. Travel is at its best when it gives you a seat at someone else's table.",
    ],
  },
];

export function getStoryBySlug(slug: string) {
  return stories.find((story) => story.slug === slug);
}