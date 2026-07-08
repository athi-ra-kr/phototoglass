# Riou Ocean Glass — Django project (Option 2)

A full **Python / Django** site: every page is a Django template, content is
managed from the **Django admin**, and the interactive **Design Studio** is
embedded as a small JavaScript island (prebuilt bundle in
`store/static/store/studio.bundle.js`).

## Requirements
- Python 3.10+

## Run locally
```bash
python -m venv venv
# Windows:  venv\Scripts\activate
# macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed                 # loads demo products / banners / collections / FAQ
python manage.py createsuperuser      # for the admin (or use the bundled one below)
python manage.py runserver
```
Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for the
content panel.

> A pre-seeded `db.sqlite3` is included with a demo admin: **admin / admin12345**.
> Change this before deploying (or delete db.sqlite3 and re-run migrate/seed/createsuperuser).

## Managing content (the admin panel)
Log in to `/admin/`. You can add/edit/delete:
- **Products** (name, type, price, gradient, image, featured, active)
- **Banners** (hero carousel slides)
- **Collections** (themed category cards)
- **FAQ** (How It Works accordion)
- **Site configuration** (brand, phone, WhatsApp, email, social links)
- **Leads** (incoming B2B quote + contact form submissions)

Changes appear on the site immediately — no code edits needed.

## Project structure
```
riou/                 Django project (settings, urls, wsgi)
store/
  models.py           content models
  admin.py            admin registrations (the content panel)
  views.py            page views + session cart
  urls.py             routes
  forms.py            quote + contact forms
  nav.py              menu structure
  context_processors.py   injects nav, site config, cart count into every template
  management/commands/seed.py   demo-content seeder
  templates/store/    all page templates (+ partials: header, footer, whatsapp)
  static/store/       app.css (theme), theme.js (dark/light toggle), studio.bundle.js (studio island)
```

## The Design Studio (JS island)
`/studio/` loads `store/static/store/studio.bundle.js`, a prebuilt React editor
mounted into `#studio-root`. To change it, edit the React source and rebuild:
```bash
# from the separate React project that produced it:
npx esbuild studio-entry.jsx --bundle --minify --format=iife \
  --loader:.js=jsx --outfile=store/static/store/studio.bundle.js
```

## Notes
- Tailwind is loaded via the Play CDN in `base.html` for zero-config styling.
  For production, compile Tailwind and remove the CDN.
- Phone / WhatsApp / email / socials are editable in admin → Site configuration.
- Cart is session-based; checkout just clears the cart (no payment gateway wired).

## Custom content dashboard (in addition to Django admin)
A branded, in-app admin lives at **/dashboard/** — styled like the site, for
non-technical staff to manage content without using Django's `/admin/`.

- Log in at `/dashboard/login/` with any **staff** account (the bundled
  `admin / admin12345` works).
- Manage **Banners, Products, Collections, FAQ**, edit **Site configuration**,
  and read incoming **Leads** (quote + contact submissions).
- Live preview of gradient + emoji while editing banners/products/collections.
- Product image uploads supported (saved to `media/`).

Two ways to manage content now:
1. **/dashboard/** — friendly branded panel (recommended for staff).
2. **/admin/** — full Django admin (power users / advanced fields).

### Giving someone dashboard access
Any user with the **staff** flag can log in to `/dashboard/`. Create one via:
```bash
python manage.py createsuperuser          # full access
```
or in Django admin → Users → add user → tick "Staff status".

## Update — Collections, Inspiration, Orders (this build)
- **Collections**: 2-level catalog. Admin adds **Categories**, then **Collections** (pick a category, upload **multiple images**, add **multiple sizes** = dimension + price + stock). Frontend: Collections menu lists categories → category page → collection detail with image gallery + size picker + **Add to cart**.
- **Cart → Orders**: placing an order creates an **Order** with line items, visible under **Orders** in the dashboard and Django admin (status editable). No payment/login yet.
- **B2B**: single page with dummy section content; the **Quote form still saves** to Leads.
- **Inspiration** sub-pages: **Blog/Tips** (backend, Markdown body, card → read more → full post), **Before & After** (backend, before+after images + caption), **Size Guide** & **Photo Preparation Guide** (static — edit the templates), **Customer Stories** (backend, image or YouTube + text + rating).
- **How It Works**: static single page (FAQ still pulls from DB).
- **About**: static page (edit `templates/store/about.html`).
- **Contact**: address, embedded **Google Maps** (set the embed URL in dashboard → Site config), WhatsApp/phone/email + working form.

### Where to manage things
Dashboard (`/dashboard/`) left menu: Banners, Products, Categories, Blog/Tips, Before/After, Customer Stories, FAQ, **Collections**, **Orders**, Leads, Site config.
Complex image/size editing for Collections also works great in Django admin (`/admin/`) via inlines.

> Markdown in blog bodies: `**bold**`, `*italic*`, blank line = new paragraph, lines starting with `- ` become bullets.

## Update — Home page, Banners, Product categories, Logo (Phase 1)
- **Logo:** drop your file at `media/logo/logo.png` — it appears in the header, footer, dashboard and login automatically. If it's missing, the ≈ mark is shown.
- **Banners are now full sections:** each banner has Title, Description, an uploaded **image (no text baked in)**, **two buttons** (text + link each), order and active. The whole left-text / right-image section swaps per slide. Edit in dashboard → Banners.
- **Product categories:** new model + dashboard menu (listed under "Product categories", above Products). Products now pick a category; the Products menu dropdown lists categories, and `/products/category/<id>/` shows a category's products with filter chips.
- **Collection categories:** renamed in the dashboard and placed directly **above Collections** in the sidebar.
- **Home page rebuilt** in this order: Banner → trust bar → animated **Design Yourself** section (CSS/JS mock, links to the studio) → Browse product categories (row + View all) → Browse collections (row + View all) → Blog & Tips (row + View all) → Customer Stories (row + View all) → How it works → FAQ → footer.

Next phases (planned): Design Studio Assets backend → data-driven front-end studio → admin product configurator + locked customer mode.

## Update — Design Studio Assets backend (Phase 2)
New **Studio assets** group in the dashboard sidebar (and in Django admin), the building blocks the studio will use later:
- **Background Shapes** — name + **priced sizes** (width × height cm + base price). Seeded: *Rectangle Landscape* & *Rectangle Portrait* (25×35, 35×50, 40×60, 60×85). Custom editor with add/remove size rows.
- **Background Images** — library of fills (uploaded images).
- **Background Colors** — palette of solid/gradient fills (CSS color or gradient string) — the colour alternative to images.
- **Background Frames** — outer border graphics, each tied to a Background Shape.
- **Portrait Shapes** — small clip shapes (e.g. Heart) with their own width/height cm + shape image.
- **Portrait Images** — library of images to drop into portrait shapes.
- **Portrait Frames** — border graphics tied to a Portrait Shape.
- **Embellishments** — stickers/decorations.

All manageable from `/dashboard/` (and `/admin/`). Pricing model: **base price lives on Background Shape + size**; a product configuration can override it later (Phase 4).

> This phase is data + CRUD only. Phase 3 wires the front-end studio to load these assets (drag/zoom/rotate/text/layers) from the backend; Phase 4 adds the admin product configurator + locked customer mode.

## Update — Studio fixes + data-driven studio (Phase 3, part 1)
**Dashboard fixes**
- Light mode now fills the **whole page** (sidebar scrolls internally; no dark strip at the bottom).
- The 8 studio-asset menus are collapsed under one expandable **"Design assets"** menu to shorten the sidebar.
- Removed the "View site" and "Django admin" links from the sidebar.

**Phase 3 — data-driven Design Studio**
- New JSON API at `/api/studio/assets/` returns all studio assets.
- `/studio/` is now a **data-driven editor** that loads from the backend:
  - Pick a **Background Shape** → size chips show **live prices**; the canvas matches the shape's aspect ratio.
  - **Background**: fill with an uploaded image or a colour/gradient.
  - **Frames**: overlay a frame for the current shape.
  - **Portrait shapes**: adds a photo slot masked to the shape; open **Images** to fill it.
  - **Images / Stickers / Text**: add layers — **drag, scale, rotate, delete**, with a **Layers** panel (select / reorder / remove). Text has font, colour and size controls.
  - **Add to cart** uses the selected shape+size price (→ becomes an Order).

> Note: this is the first working version of the studio. Frames/portrait masking look best with **transparent PNG** assets (the seeded ones are gradient placeholders). Saving a full design back to the order and the admin-side product configurator + locked customer mode are **Phase 4**.

## Update — Mobile studio + Product configurations (Phase 4 core)
**Mobile studio:** the editor now reflows on phones — canvas on top, asset panel below, and the icon rail becomes a scrollable bottom bar (with the two-line labels). Plate sizing adapts to the screen.

**Product configurations (admin-built designs):**
- On a product row in the dashboard → **Configs** → "Add configuration (opens studio)". The studio opens in **config mode**; compose a design and **Save configuration** (it's stored as JSON on the product).
- Each product can have **multiple configurations**; manage/delete them on the product's Configs page.
- **Customer side:** the product page lists configurations with a **Personalise** button that opens the studio in **locked mode** — customers can only change the **portrait image and text** (shape/background/frames/stickers are hidden). Price still varies by size.
- **Designs are saved with orders:** adding a design to the cart stores the serialized design; on checkout it's attached to the order item and shown in the dashboard order view (🎨 custom design · N layers). Pricing uses the shape+size base price (a config can carry a fixed `price_override`).

> Studio interactions are best verified in a browser. Frames/portrait masking need transparent PNG assets. Customer login + payment remain future work.

## Update — Configurator fixes + locked-mode personalisation
- **Fixed:** editing an existing configuration and clicking Save now **updates that configuration** (it no longer creates a duplicate).
- **Locked customer studio** (Personalise) now allows: **replace the photo in a portrait slot by uploading from their device**, **edit the text** the admin added (wording + style), **add stickers**, and **change the background colour**. Adding shapes/frames/portrait-slots/new text stays locked.
- **Fonts:** a set of display & script fonts (Manrope, Fraunces, Playfair, Poppins, Montserrat, Oswald, Bebas Neue, Lobster, Pacifico, Dancing Script, Georgia, Mono). The dropdown previews each option **in its own typeface**, and picking one updates the selected text **live** — for both admin and customer.
- **Colour palette** swatches now render correctly (each swatch shows its colour), in both the admin config studio and the customer locked studio.

## Update — Asset rules, connected studio, account & design PDF
**Background assets**
- **Background Shapes are fixed** (added via code). The dashboard page now only lets you **edit the price of each size** — no add/edit/delete. New shapes (e.g. Heart) are added on request with their exact dimensions/mask.
- **Background images** are now tied to a **background shape**; **portrait images** are tied to a **portrait shape**. In the studio, selecting a shape shows only its matching images/frames so they fill correctly.
- **Embellishments** now carry a default on-canvas **size** (small by default).

**Design studio**
- Rail labels written in full: Background Shape / Background Image / Background Frame / Portrait Shape / **Portrait Image** / **Portrait Frame** / Stickers / Text. **Portrait Frame is now available** in the studio.
- **Text colour**: round preset swatches (incl. gradients) for one-tap colour, plus a clearly-labelled rainbow “Custom colour” button (the old plain-white picker is gone). Multiple fonts preview in their own typeface and apply live.

**Product configurations**
- Each configuration = **one size**; the configuration is **auto-named after that size** (no name prompt). Add several configurations per product for different sizes/prices. Editing a configuration and saving **updates it** (no duplicate).
- In **locked/personalise** mode the customer can: upload their **own photo** into a portrait slot (or pick from the matching library), change **frames** and **portrait frame**, add **stickers**, **replace/restyle text** (all colours + fonts), and change the **background colour**. Shape and slots stay locked.

**Account & order PDF**
- A **My account** icon sits left of the cart; it opens a **Sign in with Google** page (placeholder — auth to be configured).
- After an order is placed, the confirmation page offers **Download your design (PDF)**; the dashboard order view has the same link. The PDF is a raster reconstruction of the saved design (looks best with transparent-PNG shape/frame assets).

## Update — Locked tabs, exact-size PDF, home grids, favicon
- **Personalise (locked) mode:** Background Image and Background Frame are now hidden — customers cannot change them. They can still change portrait photo (upload/library), portrait frame, stickers, text (colours/fonts) and background colour.
- **Design PDF = exact frame size.** The downloaded PDF page is now the real physical size of the chosen dimension (e.g. 40 × 60 cm at 150 DPI), with text/images/background scaled exactly as in the studio, and the background frame included.
- **Home layout:** Browse products = 4 per row, Browse collections = 5 per row, Blog & tips = 3 per row, Customer stories unchanged, FAQ = 2 per row.
- **Favicon:** drop `favicon.png` into `media/logo/` and it's used as the site favicon automatically.

## Update — One-row home, PDF fidelity, locked = photo/frame/text only
- **Home rows** now show a single row each: products 4, collections 5, blog 3 (extra items aren't shown on the home page).
- **Design PDF fixed.** Layer positions are stored as fractions of the plate, so the export matches the studio exactly regardless of screen size (previously items could shift off-canvas). Seeded frames are now transparent-centre PNGs so a frame never hides the design. The page is the exact physical size of the chosen dimension.
- **Personalise (locked) mode** now allows ONLY: replace each portrait photo (upload from device or pick the matching library), change the frame around each portrait, and edit text (colours/fonts). Background image, background colour, background frame, shapes, portrait shapes and stickers are all hidden, and customers can't delete the admin's layers.

## Update — Text panel on the right, taller product cards, toggle icon, PDF size
- **Text controls moved to the right column**, above Layers, and are **always visible** (no more scrolling the left rail to find Text). The left rail now ends at Stickers. On mobile the right column stacks at the bottom so text stays reachable.
- **Browse products by category** cards now have a **taller image**.
- **Theme toggle**: the sun/moon icon now sits **inside the knob** so it's clearly visible in both light and dark mode.
- **Design PDF**: text now renders at the **same size as the studio** (positions/sizes are stored as plate fractions and scaled to the exact frame size). Earlier orders made before this change won't match; new orders will. Real transparent-PNG shape/frame assets give the crispest result.

## Update — Exact exports: Download PNG + Download PDF
The design is now rendered **in the browser from the actual studio canvas** (same fonts, sizes, positions, masks, gradients) at high resolution for the chosen dimension. That image is saved with the order, so exports match the studio 1:1.
- Order confirmation page and the dashboard order view now show **Download PNG** and **Download PDF** for each personalised item.
- PNG = the exact high-res studio render. PDF = that same image on a page at the exact physical size (cm) of the chosen dimension.
- Masks/frames render crisply once real transparent-PNG shape/frame assets are uploaded (seeded placeholders are opaque).

## Update — Toggle (both icons), footer fixes
- **Theme switch** now shows **both** icons permanently (🌙 and ☀️) with the round knob sliding to the active side — so you always see which way you can switch.
- **Footer → Company**: removed the Staff dashboard link; now B2B & Trade, Inspiration, About, Contact Us.
- **Footer → social icons**: proper SVG icons for Facebook, Instagram (fixed), TikTok and YouTube. Added a `youtube` link field to Site config (dashboard → Site config).
