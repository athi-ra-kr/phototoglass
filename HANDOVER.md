# Riou Ocean Glass — Project Handover (Exhaustive)

> Purpose: this document lets a brand-new chat (or another developer) continue the
> project with zero prior context. If a chat session is lost, **upload the latest
> project zip + this file** and say "continue from HANDOVER.md".

_Last updated: keep this in sync whenever code changes (the assistant appends a
changelog entry at the bottom each update)._

---

## 1. What this project is

**Riou Ocean Glass** is a Django website + **custom design studio** for a printed‑glass
art/gift business in **Mauritius**. Customers design printed‑glass pieces online
(photos, text, frames, stickers on a chosen shape/size), the studio exports a
**high‑resolution image and a print‑size PDF**, and orders are placed on the site.
Staff manage everything from a custom dashboard.

**Brand / design system**
- Fonts: **Fraunces** (display) + **Manrope** (body). Studio text also offers Playfair,
  Poppins, Montserrat, Oswald, Bebas Neue, Lobster, Pacifico, Dancing Script, Georgia, Mono.
- Accent: teal `#4fe3cf` / `#0fb6a2`; dark + light themes (toggle in header, persisted).
- Currency: **Mauritian Rupee**, always shown with the prefix **`Rs`** (e.g. `Rs 49`).
- Tailwind via Play CDN + a custom `app.css`. Vanilla JS (no build step for the studio).

---

## 2. Tech stack & environment

- **Django** (requirements pinned to `Django>=4.2,<5.1` so it runs on Python 3.8+;
  on Python 3.10+ it installs Django 5.x). **Pillow** for image/PDF generation.
- Database: **SQLite** (`db.sqlite3`, shipped seeded in the zip).
- No Node/React build step. The old `store/static/store/studio.bundle.js` is **legacy
  and unused** — the live studio is vanilla JS inside `store/templates/store/studio.html`.

### Fixed shapes now come from a data migration
The canonical background + portrait shapes/sizes are created by **`migrate`** (migration
`store/migrations/0003_seed_studio_shapes.py`, idempotent via `get_or_create`). So production needs
only `migrate` for shapes — **no `seed`**. `seed` is now for demo content only. See `DEPLOY.md`.
To change shapes later, ship a NEW migration copying that file's pattern.

### Run it (macOS / Linux)
```bash
cd riou-django
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000 — site. Dashboard: http://127.0.0.1:8000/dashboard/
(**admin / admin12345**). Django admin: /admin/.

### Fresh rebuild of demo data (if needed)
```bash
rm -f db.sqlite3 store/migrations/0001_initial.py
rm -rf media && mkdir -p media/logo
python manage.py makemigrations store
python manage.py migrate
python manage.py seed
DJANGO_SUPERUSER_PASSWORD=admin12345 python manage.py createsuperuser --noinput --username admin --email a@e.com
```

### Brand assets the owner drops in (optional, auto‑detected)
- `media/logo/logo.png`  → light‑mode logo
- `media/logo/logo2.png` → dark‑mode logo
- `media/logo/favicon.png` → site favicon
If a logo exists, the header/footer brand **text is hidden** and the logo shows
(switches by theme). If none exist, a `≈` tile + brand text is shown.

### Common gotchas
- **"No module named django" / "Could not find Django==5.0.6"** → the machine's Python
  is < 3.10. Already handled by the loosened requirement (`Django>=4.2,<5.1`). Reinstall.
- Activate venv with `source venv/bin/activate` (not `source` on Windows).
- `pip install ... --break-system-packages` only needed on some managed Pythons.

---

## 3. Project structure

```
riou-django/
  manage.py  requirements.txt  README.md  HANDOVER.md  db.sqlite3
  riou/            settings.py  urls.py  wsgi.py  asgi.py
  media/           uploaded + seeded images (logo/, products/, studio/, orders/, …)
  store/
    models.py            all models (see §4)
    views.py             public site + studio + cart/checkout + exports (see §6)
    dashboard.py         staff dashboard, generic CRUD registry (see §7)
    urls.py              URL map (see §5)
    context_processors.py  site() → NAV, SITE, cart_count, logos, favicon
    forms.py             (lead/contact forms etc.)
    pdfgen.py            server-side render + PNG→PDF helpers (see §8)
    admin.py             Django admin registrations
    templatetags/md.py   tiny markdown filter (**bold**,*italic*,paragraphs,'- ' bullets)
    management/commands/seed.py   demo data + placeholder image generators
    static/store/        app.css, theme.js, (legacy studio.bundle.js)
    templates/store/     public pages + partials/
    templates/dashboard/ staff dashboard pages
```

---

## 4. Data models (`store/models.py`)

**Site / content**
- `SiteConfig` (singleton via `.get()`): brand, tagline, phone, whatsapp, email,
  address, map_embed, **facebook, instagram, tiktok, youtube**, **logo_light, logo_dark, favicon** (uploads).
- `Banner`: title, description, image, gradient, btn1_text/link, btn2_text/link, order, active.
- `ProductCategory`: name, description, order, active. (`products` reverse FK)
- `Product`: name, category(FK ProductCategory), **product_type** (`fixed`|`personalise`), price, motif, gradient,
  image, description, stock, active, order, created.
  - **Fixed** = buy directly (Add to cart shown, no Configs). **Personalise** = customer must
    personalise via the studio; **no direct Add to cart** — either an existing `ProductConfig`
    (personalise link) or, if none yet, a "Design this in the studio" link. Enforced both in the
    template and server-side (`product_detail` view rejects a POST for a personalise product).
  - **Note:** `motif`/`gradient` exist but are **not editable in the dashboard** (products
    use `image`). Props: `type_label` (=`get_product_type_display()`), `is_personalise`,
    `category_name`, `thumb_url`. (`configs` reverse FK)
  - Dashboard "Configs" action only shows for Personalise products (Fixed products can't have configs).
- `Faq`: question, answer, order.
- `Lead`: kind(quote|contact), name, email, company, segment, quantity, message, created.

**Collections (gallery, not the studio)**
- `CollectionCategory`: name, description, order, active. (`collections` reverse FK)
- `Collection`: category(FK), title, description, active, created.
- `CollectionImage`: collection(FK), image, order.
- `CollectionDimension`: collection(FK), width_cm, height_cm, price, stock.

**Inspiration**
- `BlogPost`: title, excerpt, image, body(markdown via `md` filter), active, created.
- `BeforeAfter`: title, caption, before_image, after_image, order, active.
- `CustomerStory`: name, location, image, youtube_url, story, rating, order, active.
  Prop: `youtube_embed`.

**Orders**
- `Order`: created, status(received|…), customer_name, total. (`items` reverse FK)
- `OrderItem`: order(FK), title, detail, qty, unit_price, **design(JSONField)**,
  **render(ImageField → `orders/`)**. Prop: `line_total`.
  - `design` = the serialized studio design (see §9). `render` = the **exact high‑res PNG**
    captured from the browser studio canvas (source of truth for downloads).

**Studio assets** (these power the design studio)
- `BackgroundShape`: name, order, active. (`dimensions`, `bg_images`, `frames` reverse FKs)
  - **Fixed in code** — admin can only edit dimension prices, not add/edit/delete shapes.
- `BackgroundShapeDimension`: shape(FK), width_cm, height_cm, base_price. (`label` prop e.g. "40 × 60 cm")
- `BackgroundImage`: name, **dimension(FK BackgroundShapeDimension, REQUIRED)**, image, order, active.
  - Every image belongs to exactly one size; `shape` is set automatically from the dimension (kept for grouping/API). Shows in the studio only for that exact size.
- `BackgroundColor`: name, color(CSS hex or `linear-gradient(...)`), order, active.
- `BackgroundFrame`: **dimension(FK BackgroundShapeDimension, REQUIRED)**, name, image (transparent‑centre PNG), order, active.
  - Same rule as BackgroundImage: one size per frame; `shape` auto-set from the dimension.
- `BackgroundStand`: name, image (photo of the stand), **shapes (M2M → BackgroundShape, tick
  any/all)**, order, active. Dashboard form renders `shapes` as checkboxes. Sits in the sidebar
  **right after Background Frames**. Reverse FK on `BackgroundShape` is `stands`.
  - **Studio (free/config mode):** as soon as a Background Shape is selected, if any Stand
    includes that shape, a **read-only** "Stand" card (name + photo) shows in the right column —
    automatic, updates live as the shape changes, nothing for the customer to pick.
  - **Personalise/locked studio:** shows the stand for whatever shape the admin's config used
    (same mechanism — `loadDesign()` selects the shape, which triggers the stand lookup).
  - **Product page:** each "Personalise a design" config link also shows its matching stand
    read-only ("Comes with: <name>"), computed server-side in `product_detail` from the config's
    saved shape — not editable by the customer.
  - (This model was originally built tied to Background *Frame* — corrected via migration `0005`,
    which safely **renames** the old `FrameStand` table rather than dropping it, so any real stand
    a live admin already created keeps its name/photo. Only the frame↔shape relationship itself
    can't be carried over automatically — re-tick shapes once per existing stand after this update.)
- `PortraitShape`: **hard-coded** (like background shapes). name, **key** (coded outline: square|heart|circle|oval), order, active. No image, no price; can't be added/edited/deleted in the dashboard. (`dimensions`, `images`, `frames` reverse FKs)
- `PortraitShapeDimension`: shape(FK), width_cm, height_cm (**one small size per shape**; no price). `label` prop. Photo is zoom/rotate-able in the studio so a single size suffices.
- `PortraitImage`: name, **dimension(FK PortraitShapeDimension, REQUIRED)**, image, order, active. `portrait_shape` auto-set from dimension.
- `PortraitFrame`: **dimension(FK PortraitShapeDimension, REQUIRED)**, name, image, order, active. `portrait_shape` auto-set.
  - The shape *outline* (heart/circle/etc.) is **coded in the studio** (SVG clip-path + canvas Path2D), not uploaded — so masks are crisp in studio and export. The uploaded image is just the photo that fills the shape; the frame is an overlay PNG.
- `Embellishment` (sticker): name, image, **width, height** (default on‑canvas px), order, active.
- `ProductConfig`: product(FK), name, **design(JSONField)**, price_override, order, active, created.
  - An admin‑built design template attached to a product. One config = **one size**;
    its `name` is auto‑set to the dimension label. Customers personalise it (locked mode).

**Asset → shape connections** (important): in the studio, when a background shape is
selected, only its matching `BackgroundImage`/`BackgroundFrame` show; portrait images/
frames are filtered to the selected portrait slot's `PortraitShape`.

---

## 5. URL map (`store/urls.py`)

**Public**: `/` home · `/products/` · `/products/category/<pk>/` · `/product/<pk>/` ·
`/collections/` · `/collections/<pk>/` (category) · `/collection/<pk>/` ·
`/b2b/` · `/inspiration/` (+ `/blog/`, `/blog/<pk>/`, `/before-after/`, `/size-guide/`,
`/photo-guide/`, `/customer-stories/`) · `/how-it-works/` · `/about/` · `/contact/` ·
`/account/` (Google sign‑in placeholder).

**Studio / cart / orders**:
- `/studio/` — the editor. Query params: `?mode=free|config|locked`, `?product=<id>`, `?config=<id>`.
- `/api/studio/assets/` — JSON of all active studio assets.
- `/studio/add/` (POST) — add current design to cart (carries `design` + rendered `image`).
- `/studio/save-config/` (POST, staff) — create/update a `ProductConfig`.
- `/cart/`, `/cart/remove/<key>/`, `/checkout/`.
- `/order/<pk>/design.pdf` — all items as one PDF.
- `/item/<pk>/design.png` and `/item/<pk>/design.pdf` — per‑item downloads (exact size).

**Dashboard** (staff): `/dashboard/` overview · `/dashboard/login|logout/` ·
`/dashboard/site/` · `/dashboard/leads/` · `/dashboard/orders/` (+ `/<pk>/`) ·
collections custom CRUD · `/dashboard/shapes/` (price‑only) ·
`/dashboard/products/<pk>/configs/` · `/dashboard/config/<pk>/edit|delete/` ·
**generic CRUD**: `/dashboard/<key>/` list, `/new/`, `/<pk>/edit/`, `/<pk>/delete/`.

---

## 6. Public views (`store/views.py`)
`home, products, products_category, product_detail, collections, category,
collection_detail, b2b, inspiration, blog, blog_detail, before_after, size_guide,
photo_guide, customer_stories, howitworks, about, contact, account, studio,
studio_save_config, studio_assets, studio_add, cart_remove, cart, checkout,
order_design_pdf, item_png, item_pdf` + helper `_add(...)`.

**Cart** is a session dict keyed per add; each line stores name, detail, price, qty,
grad, motif, img, **design** (JSON string), **render** (PNG dataURL).
**checkout** creates `Order` + `OrderItem`s, parses `design` JSON, decodes the `render`
dataURL and saves it to `OrderItem.render`, then shows `order_success.html` with
per‑item **Download PNG / Download PDF** buttons.

---

## 7. Staff dashboard (`store/dashboard.py`)
- Login‑gated (`@staff_required`). Sidebar built by `_nav(active)`; the studio‑asset
  items are collapsed under one expandable **"Design assets"** group.
- **Generic CRUD `REGISTRY`** drives most models. Keys → model/fields:
  `banners, productcats, products, categories(CollectionCategory),
  blog, beforeafter, stories, faqs, bgimages, bgcolors, bgframes, portraits,
  portraitimages, portraitframes, stickers`.
  - `products` fields exclude motif/gradient (image‑based).
  - `bgimages`/`bgframes`/`portraitimages`/`portraitframes` forms show **`dimension` only** (required; shape auto-set).
    Portrait **shapes** are fixed in code — no CRUD; a read-only **Portrait Shapes** page (`dash_pshapes`,
    `/dashboard/portrait-shapes/`) lists the 5 shapes + their sizes. `stickers` includes `width/height`.
- **Custom views**: `collection_list/edit/delete` (+ image/dimension deletes),
  `shape_list` (**price‑only** editor — POSTs `price_<dimid>` values; shapes are fixed),
  `product_configs`, `config_edit` (name, price_override, active, order), `config_delete`,
  `orders`, `order_detail` (shows custom‑design note + PNG/PDF download links),
  `leads`, `site_config`.

---

## 8. Server‑side rendering / PDF (`store/pdfgen.py`)
- `DPI = 150`. cm→px: `px = cm/2.54*DPI`.
- `_render(design)` — best‑effort server raster of a design (fallback only).
- `_item_image(item)` — returns the **stored browser render** (`item.render`) if present,
  else falls back to `_render(item.design)`.
- `_size_to_dim(img, design)` — resizes to the exact dimension (cm) at 150 DPI.
- `build_item_pdf(item)` / `build_order_pdf(order)` — embed the render(s) into a PDF
  at the exact physical size.
- **Key point:** the trustworthy export is the **browser render** stored on the order.
  The server PDF just wraps that PNG at the right page size, so it matches the studio 1:1.

---

## 9. The Design Studio (`store/templates/store/studio.html`, vanilla JS)

Loads `/api/studio/assets/` and renders an editor. Left rail tabs (icon + 2‑line label):
**Background Shape, Background Image, Background Frame, Portrait Shape, Portrait Image,
Portrait Frame, Stickers**. The **Text** controls live in the **right column above Layers**
(always visible). Right column also has the **Layers** list (select / reorder / delete).

**State `S`**: `{shape, dim, fill, frame, layers[], sel, z, plateW, plateH}`.
Each layer: `{id, type:'image'|'sticker'|'portrait'|'text', x,y,w,h,rot, src, mask,
pshape, pframe, text, color, font, size, name}` (live values are **absolute px** on the plate).

**Coordinates are stored as plate FRACTIONS** (resolution‑independent):
`serialize()` divides x/w by `plateW`, y/h/size by `plateH` and sets `norm:true`,
plus `shape, dim, dim_w, dim_h(cm), fill, frame, pw, ph`. `loadDesign()` multiplies
back by the current plate size. This is what makes a config built at one screen size
render correctly at another and in the PDF. **Don't revert to absolute px.**

**Modes** (`?mode=`):
- `free` — Design Yourself. Primary button = **Add to cart**.
- `config` — admin building a `ProductConfig` (opened from a product's Configs page).
  Primary = **Save configuration** (auto‑named after the chosen size; updates if `config_id` set).
- `locked` — customer personalising a config. **Only** Portrait Image (incl. device upload),
  Portrait Frame, and Text are available; shape/background image/background colour/background
  frame/portrait shape/stickers are hidden; the admin's layers can't be deleted.

**High‑res export (client‑side):** `renderPNG()` draws the design onto an off‑screen
canvas at `dim_w×dim_h` cm @150 DPI using the **real fonts**, mask compositing
(`destination-in`), portrait frames, gradients, rotation — i.e. pixel‑identical to the
studio. On **Add to cart**, this PNG (dataURL) is sent in the hidden `image` field and
saved to `OrderItem.render`. Downloads serve that image (PNG) or wrap it in a PDF (exact cm).

**Asset connections in the UI:** background images/frames filter by the selected
`BackgroundShape`; portrait images/frames filter by the selected portrait slot's
`PortraitShape`.

---

## 10. Theme toggle, logos, favicon, footer
- **Theme toggle** (`header.html` + `app.css` + `theme.js`): a pill with **both** 🌙 and ☀️
  always visible; a teal **knob slides** to the active side. Theme persisted in localStorage,
  applied as `data-theme` on `.rog`. (History: an earlier single‑icon/CSS approach failed;
  current both‑icons + sliding knob is the correct one.)
- **Logos**: `partials/logo.html` include (`{% include ... with h=NN %}`); shows light/dark
  logo by theme, hides brand text when a logo is present.
- **Favicon**: auto‑linked in `base.html` when `media/logo/favicon.png` exists.
- **Footer**: Explore + **Company (B2B & Trade, Inspiration, About, Contact Us — no staff link)**
  + Contact columns; social icons are SVGs for Facebook, Instagram, TikTok, YouTube.

---

## 11. Home page layout rules (`home.html`)
Banner carousel → trust bar → animated "Design Yourself" mock → **Browse products by
category (4 per row, 1 row)** → **Browse collections (5 per row, 1 row)** →
**Blog & tips (3 per row, 1 row)** → Customer stories → How it works → **FAQ (2 per row)**.
Product‑category cards use a taller image plate.

---

## 12. Known limitations / not done yet
- **Portrait shapes are now coded** (square/heart/circle/top-wave/oval) via clip-path/Path2D,
  so they render crisply in studio and export — no transparent-PNG mask needed. **Background**
  shapes are still plain rectangles (the plate); their seeded frame/image placeholders are opaque,
  real transparent-PNG **background frames** still look best.
- **No payments** — checkout records an order without auth/payment.
- **No real auth yet** — `/account/` is a "Sign in with Google" placeholder.
- Seeded prices (Rs 49/69/89/129) are demo numbers; edit in dashboard → Design assets →
  Background Shapes (price‑only).
- The assistant can read code/zip but **cannot see the rendered browser** — send
  screenshots for visual/interaction issues.

---

## 13. Pending / next steps (roadmap)
1. **Google login** (OAuth) → needs client ID/secret + authorised redirect URIs.
2. **My account** area: profile, **My orders** (link orders to the logged‑in user going
   forward), **My addresses** (CRUD, default address, use at checkout).
3. Tie `Order` to `user` (add FK) once auth exists.
4. New **Background Shapes** on request (e.g. **Heart**) — owner provides exact
   dimensions/side distances/orientation + a **transparent‑PNG mask**; added in code/seed.
5. Owner to provide `logo.png`, `logo2.png`, `favicon.png`.
6. Payment gateway.

---

## 14. How to resume in a NEW chat
1. Upload the **latest project zip** (the one the assistant last gave you, or your current
   local copy if you changed things).
2. Upload **this `HANDOVER.md`** (it's also inside the zip at the project root).
3. Say: *"Continue the Riou Ocean Glass project — read HANDOVER.md and the zip."*
4. For any visual bug, attach a **screenshot**.
The assistant works in a Linux sandbox: it unzips to `/home/claude/riou-django`, edits,
runs `manage.py check`/tests, re‑seeds, and returns a new zip via the file panel.

---

## 15. Changelog (high‑level, newest last)
- Phase 1–2: home rebuild, full Banner model, Product Categories, dual logos; studio asset
  models + dashboard CRUD.
- Phase 3: assets JSON API + data‑driven vanilla studio (shapes/sizes/price, bg image/colour,
  frames, portraits, stickers, text; drag/scale/rotate/layers); mobile layout; rail labels.
- Phase 4: `ProductConfig` (admin config mode, customer locked mode), designs saved into orders,
  per‑config pricing; product form drops motif/gradient (image‑based); currency switched to **Rs**.
- Fixes: light‑mode dashboard bg; collapsed "Design assets" sidebar; removed View site/Django
  admin links; config save updates (no duplicate); multi‑font + live preview; colour swatches +
  presets + custom picker; locked‑mode restricted to portrait image/frame + text; background
  shapes fixed (price‑only); assets connected to shapes; sticker sizes; transparent seeded frames;
  **coordinates normalised to plate fractions** (fixes PDF/text drift); exact‑size PDF.
- Exports: **client‑side high‑res render** → `OrderItem.render`; **Download PNG + Download PDF**
  on order page + dashboard, both at the exact chosen dimension.
- UI: taller product cards; **both‑icon sliding theme toggle**; footer Company menu
  (Contact Us, no staff link) + proper social SVGs incl. **YouTube**; `SiteConfig.youtube`;
  My‑account icon in header; favicon support; `requirements.txt` → `Django>=4.2,<5.1`.
- Per-size backgrounds: **Background Image** and **Background Frame** gained an optional
  **dimension** link. Set it → the image/frame shows only for that exact size in the studio;
  leave blank → shows for all sizes of the shape. Dimension dropdown reads "Shape · Size".
- Per-size backgrounds finalised (**Option B**): the dimension link on **Background Image**
  and **Background Frame** is now **required** (no "all sizes"). The form shows only the
  Dimension dropdown ("Shape · Size"); `shape` is auto-set from it. The studio shows a
  background image/frame only for its exact size.
- **Portrait shapes reworked**: now hard-coded (Square, Heart, Circle, Top wave, Oval) with a
  coded outline (`key`) used as an SVG clip-path in the studio and a canvas Path2D in the export —
  fixes the old "circle prints as a square". Added `PortraitShapeDimension` (small sizes, no price).
  Portrait **Image** and **Frame** are now tied to one shape+size (required, dimension-only form);
  studio shows a size-chip picker and filters images/frames by the selected size; photo can be
  replaced; portrait can be moved/scaled/rotated. Dashboard Portrait Shapes is read-only.
- Portrait shapes trimmed to **4** (Square, Heart, Circle, Oval — removed Top wave) and each now has a
  **single size** (the smaller one). Studio shows a **shape preview** when picking a portrait shape and
  **no size selector** for portrait images/frames — they're just sorted and shown for the shape (the one
  size is handled in the backend).
- Fixed **RequestDataTooBig** on Add to cart: raised `DATA_UPLOAD_MAX_MEMORY_SIZE`/`FILE_UPLOAD_MAX_MEMORY_SIZE`
  to 64 MB and switched the studio proof export to **JPEG (q0.9)** — same resolution, ~5–10× smaller payload
  and storage. `OrderItem.render` is now a .jpg; downloads send the correct content type; PDF embeds it as before.
- **Rectangle Landscape** background sizes changed to true landscape: 35×25, 50×35, 60×40, 85×60 cm
  (Rs 49/69/89/129). Rectangle Portrait unchanged. Matches the hard-coded landscape frames.
- **Mobile menu**: parent items with submenus (Products, Collections, Inspiration) are now collapsible
  `<details>` accordions with a rotating arrow — no longer a long flat list. Plain items stay as links.
- **Logo & favicon uploads** added to dashboard **Site config** (`logo_light`, `logo_dark`, `favicon`).
  Resolution order: uploaded SiteConfig image → else the `media/logo/{logo.png,logo2.png,favicon.png}` file
  convention → else brand text. So brands can be set from the dashboard with no server file access.
- **Shapes moved to a data migration** (`0003_seed_studio_shapes`): Rectangle Landscape/Portrait + the
  4 portrait shapes and all sizes are created by `migrate`, idempotently (safe on live DB, no dup, no delete).
  Deploy needs only `migrate` for shapes; `seed` is demo-content only. Added `DEPLOY.md`.
- **Logo/favicon uploadable** from dashboard Site config (see above).
- **Seven-item update (migration `0004_frame_stand_and_product_type`):**
  1. **WhatsApp floating button removed** site-wide (`base.html` no longer includes the floating
     icon block). Footer/Contact page WhatsApp *links* (contact info) were left as-is — only the
     floating button was removed. `partials/whatsapp.html` still exists but is unused; safe to
     delete or re-enable by restoring the `{% include %}` in `base.html`'s `whatsapp` block.
  2. **Frame Stands** (new): dashboard → Design assets → **Frame Stands** (last item, below
     Embellishments). Admin ticks which Background Frame(s) a stand fits (checkboxes, no size
     picker) + name + photo. Exposed via `/api/studio/assets/` as `frame_stands`. See model notes.
  3. **Dimension lock + Reset**: once a shape/size is chosen and the customer/admin touches any
     other panel (background image/frame/portrait/stickers) or adds any layer/text, the size chips
     **lock** (`S.dimLocked`, disabled + 🔒 hint) — matches `MODE==="locked"` behaviour that already
     existed for customer personalise mode. A **Reset** button next to the size row
     (`#st-reset`) clears the whole design client-side and starts over from shape selection.
     Reset is hidden in `MODE==="locked"` (can't wipe the admin's config). Editing an existing
     config also arrives locked (it already has a size/content).
  4 & 6. **Zoom inside portrait shape**: a "Zoom photo" slider (1×–3×) in the Portrait Image panel
     scales the photo *inside* its fixed shape (`L.zoom`, CSS `transform:scale()` on the inner
     `<img>`, independent of the outer resize handle which still resizes the shape/frame box).
     Persisted in `serialize()`/`loadDesign()` and baked into the high-res PNG/PDF export
     (`drawImageLayer` scales about the clip's center to match the on-screen crop exactly).
     Works in both the free/config studio and the customer's locked/personalise studio (same
     Portrait Image panel). Replacing the photo resets zoom to 1×.
  6. **Stand display (locked studio)**: read-only "Stand" card in the right column — shown
     automatically when the design's Background Frame has a `FrameStand` linked to it (via
     `updateStandInfo()`, matched by frame URL → frame id → stand.frames). Not selectable by the
     customer; purely informational, driven entirely by what the admin ticked in step 2.
  5. **Product type simplified**: `ptype`+`variant` replaced by a single `product_type`
     (`fixed`|`personalise`). **Fixed** → normal Add to cart, no Configs. **Personalise** → no
     direct Add to cart anywhere (template + server-side guard); customer goes through an existing
     `ProductConfig` (if any) or a "Design this in the studio" link if none exist yet. Dashboard's
     "Configs" action only appears for Personalise products.
  7. **`featured` removed completely** from `Product` and `Collection` (field dropped via
     migration; it was never used for any display logic, so this is a clean removal).
  - Model change → **no fresh DB needed, safe on a LIVE database with real orders**: migration
    `0004` first adds `product_type`, then **backfills it from the old `ptype`** for every existing
    Product (`none`→`fixed`, `partial`/`full`→`personalise`) via a `RunPython` step, THEN drops the
    old `ptype`/`variant`/`featured` columns. So existing products keep their correct type
    automatically — no manual re-tagging needed after `migrate`. Verified against a simulated
    pre-0004 database with real rows before shipping.
- **Deployment hardened for the live server** (`production.photo2glass.mu`):
  - `settings.py` now reads `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS` from environment variables
    (`.env` on the server, loaded by `deploy.sh` and via `EnvironmentFile=` in gunicorn's systemd
    unit), with safe dev defaults when unset — so `settings.py` never needs server-specific
    hand-edits again and `git pull` stays conflict-free. Added `.env.example` (template, committed)
    and `.gitignore` now excludes `.env`, `*.sqlite3`, `staticfiles/`.
  - Added `STATIC_ROOT` (`BASE_DIR/staticfiles`) matching the convention already used on the
    live server.
  - Added **`deploy.sh`** — one command (`./deploy.sh` from the project folder) that: backs up
    `db.sqlite3` + `media/` first (always, timestamped, auto-pruned to the newest 10), refuses to
    run over uncommitted changes or if the DB/media are ever accidentally tracked by git, pulls
    with `--ff-only` (never auto-merges on production), installs deps, migrates, collectstatic,
    syncs static to nginx's folder, restarts gunicorn, and verifies it came back up. Tested against
    a simulated copy of the live server's exact setup (real-sized DB, git remote, diverged-history
    and dirty-tree scenarios) before shipping.
  - See `DEPLOY.md` for the full one-time `.env`/gunicorn/nginx setup and the restore-from-backup
    steps.
- **Fixed confusing frame naming**: `BackgroundFrame.__str__` and `PortraitFrame.__str__` now
  always show `"{name} — {dimension.label}"` (e.g. "Thin Gold — 35 × 25 cm") instead of relying on
  the size being manually typed into the free-text `name` field. Demo seed frame names simplified
  to plain style names ("Thin Gold", "Simple White", "Classic Black", "Rustic Wood") since the
  dimension now always displays correctly on its own. This is what shows in the Frame Stands
  checkbox list, the Background Frames dashboard list, and Django admin.
  - Note: this doesn't rename frames already created before this update — only affects display
    going forward (and any newly seeded demo data).
- **Frame Stand display in the studio — re-verified, no bug found**: reproduced the exact flow
  (create a Frame Stand in the dashboard → tick Background Frames → save → open the studio → pick
  a linked frame) via automated tests in both free/config and locked (personalise) mode; the read-
  only "Stand" card appears correctly every time. If it's still not appearing after this update,
  the most likely cause is the studio tab having loaded its asset list *before* the stand was
  saved (assets are fetched once on page load) — refresh the studio page after adding/editing a
  stand in the dashboard. If it persists after a refresh, capture the browser console for errors.
- **Corrected: Stands are for Background Shapes, not Background Frames.** Renamed
  `FrameStand` → `BackgroundStand` (migration `0005`, safely renames the live table rather than
  dropping it — preserves any real stand's name/photo; only its shape-linkage needs re-ticking
  once). Dashboard position moved to **right after Background Frames** (was previously last, after
  Embellishments). Studio now shows the matching stand as soon as a **Background Shape** is
  selected (was previously tied to selecting a frame). Also added: the matching stand now shows
  **read-only on the product page** next to each personalise config ("Comes with: <name>"), not
  just inside the studio.
