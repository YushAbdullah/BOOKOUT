# BOOKOUT

A cosy reading game. Pick a place to read, go through its ritual, and read real free books inside the app while the venue runs its day around you.

## How it plays

| Venue | Ritual | Timer | Break prompts |
|---|---|---|---|
| **Kopi & Pages** (coffee shop, 7 AM to 11 PM) | Order a drink: espresso 10 min up to a pot of tea 60 min | The cup drains as you read | Mineral water, washroom, aesthetic photo |
| **The Commons Library** (8 AM to 10 PM) | Check in for 30 min to 3 hours, borrow books, buy a membership with points | Ring counts down to check-out; the library closes at closing time | Stretch, water fountain, canteen meal (every 25 min) |
| **Bun & Chapter** (burger joint, 24 hours) | Order a meal: fries, nuggets, burger combo, big feast | Each bite on your tray is a slice of time | Free refill, wash your hands, tray-and-book photo |

Feels like a real place:

- **Walk the street**: the home screen is a top-down town (Jalan Buku) you walk around with WASD, arrow keys, taps or the on-screen pad. Walk into Kopi & Pages, The Commons Library or Bun & Chapter and up to the counter to order or check in. Readers sit at tables with real books and chat in speech bubbles, people cross at the zebra crossings, cars stop for you, Oyen the cat wanders the park, the Passport Office opens your badges, and a book swap box and Pak Mat's book cart hand out daily treats and tips. Closed venues pull their shutters, and the whole street darkens at night with lamps and lit windows. Pick your hair, hijab, skin and top under **Look**.
- **Walk-in scenes**: each venue is drawn as a room (café window and chalkboard, library shelves with a real-time clock, diner neon and menu screen) and gets darker at night.
- **Staff who talk to you**: Aina the barista, Encik Hafiz the librarian and Jay at the diner greet you by name, react to your order and book, call your breaks, and say goodbye. Turn on **Voice** to hear them through your browser's built-in speech.
- **Sound**: register ka-ching, coffee pour and steam, library stamp and scanner beep, fryer sizzle and order bell, page flips, plus quiet background sound for each venue. All generated in the browser, no audio files.
- **A real book**: pull books off wooden shelves by their spines, watch the cover open, and turn pages with a 3D flip (swipe, tap the page edges, or use arrow keys). Text is laid out to fit each page, with chapter openings, drop caps, running heads and page numbers. Two-page spread on wide screens, one page on phones.

Game layer:

- **Points**: 1 per focused minute, break bonuses, finish bonus, last-page bonus. Library members earn 1.25× (Silver) or 1.5× (Gold).
- **Levels**: Curious Browser → Page Turner → Café Regular → Bookworm → Chapter Chaser → Library Legend → Literary Royalty.
- **Streaks**: daily streak with a growing bonus.
- **Daily quests**: read 20 minutes, take a break when asked, finish one order or check-in.
- **16 badges**, venue passport stamps, and a photo gallery of polaroid-style "aesthetic shots" (illustrated, or with your own photo).
- **Library card**: Visitor borrows 1 book, Silver (150 pts) 3, Gold (400 pts) 6 with 24-hour access. Books are due in 7 days; returning on time pays 15 points.
- The timer pauses when you switch tabs, so points mean real reading.

Books come from **Project Gutenberg**. Each of the 12 categories opens with hand-picked classics that show instantly, then more books load from the free **Gutendex** API, and you can search any title or author. Lists and the book you are reading are cached on your device. A small offline "Pocket Poems" book always works.

## Free stack

- Plain HTML, CSS and JavaScript in one `index.html`. No build step, no server, no accounts.
- Progress is saved in the browser (`localStorage`).
- Font: Outfit (Google Fonts, open licence), the free fallback for Gilroy in the design system.
- Books: a free GitHub Action (**Fetch books**, `.github/workflows/fetch-books.yml`) copies about 100 public-domain books from Project Gutenberg into `books/` and writes `books/catalog.json`. Those open instantly from your own site. It reruns monthly, or when `books/picks.json` changes, or from the Actions tab → Fetch books → Run workflow.
- To add a book to the shelves, add its Gutenberg ID to `books/picks.json`.
- Searching the wider catalogue uses the free [Gutendex](https://gutendex.com) API; those books download through free CORS proxies and can be slow.

## Run it

Open `index.html` in a browser. That's it.

For testing, turn on **Demo speed** in Passport → Settings (time runs 30× faster), and turn off **Realistic opening hours** to enter closed venues.

## Free hosting

**GitHub Pages** (recommended, since the code is already here):
1. Repo → Settings → Pages.
2. Source: *Deploy from a branch*, branch `main`, folder `/ (root)`, Save.
3. After about a minute the site is live at `https://yushabdullah.github.io/BOOKOUT/`.

Alternatives, all free: Cloudflare Pages, Netlify (drag the folder onto app.netlify.com/drop), Vercel.

## Ideas for next steps

- Accounts and cloud sync with Supabase or Firebase free tier, plus friends and leaderboards.
- A tiny Cloudflare Worker (free) as your own CORS proxy, so book downloads never depend on public proxies.
- More sources: Open Library / Internet Archive reader, Standard Ebooks (beautifully formatted public domain).
- More venues: night train, beach hut, rooftop garden; unlock them with levels.
- Installable PWA with offline books.
