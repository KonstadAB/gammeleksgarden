# HANDOFF – gammeleksgården.se

Senast uppdaterad: 16 nov 2026 (åtgärder efter juryjämförelsen med geghotel.se, se nedan). Före det 26 okt 2026 (HQ uppdrag #6).

## Läget

- Statisk sajt i tio språk (sv i roten, `en/ da/ nb/ fi/ de/ nl/ fr/ es/ it/`), 19 sidor per språk plus 404 och en exempelsida.
  Publiceras med GitHub Pages (`CNAME` = `xn--gammeleksgrden-uib.se`, `.nojekyll`). Adresserna saknar `index.html`/`.html` (t.ex. `/rum/comfort`).
- **Sajten är dold för sökmotorer.** Alla sidor har `<meta name="robots" content="noindex, follow">`. Den spärren är kvar.
  `robots.txt` i roten är medvetet öppen (`Allow: /`): spärrar man med `Disallow` kan Google inte läsa noindex,
  och adresserna kan då ändå hamna i sökresultaten utan beskrivning.
- Ingen sitemap ligger i roten före lansering. Den färdiga finns i `lansering/`.
- HTML-filerna ser ut att vara genererade av en sajtgenerator som inte finns i repot (gamla kommentarer nämner `site.launched`).
  Ändringarna nedan är gjorda direkt i HTML. **Finns generatorn någonstans måste ändringarna föras in där också**, annars skrivs de över nästa gång sajten byggs.
  Kör `python3 verktyg/seo.py kontroll` efter varje bygge.

## Gjort i uppdrag #6 (SEO-förberedelse)

1. **Meta-texter:** 178 meta description (och `og:description`) var kortare än 120 eller längre än 160 tecken. De är nu kortade eller utökade till 120–160 tecken i alla tio språk,
   med samma innehåll i sak. Uppgifterna kommer från sidornas egna texter. Alla title och description är unika. Varje sida har en H1, canonical och hreflang för alla tio språk plus x-default (→ svenska).
   Alla bilder har alt-text. Tom alt finns bara på dekorativa sigill och ska vara tom.
2. **Strukturerad data (JSON-LD):**
   - `Hotel`/`LodgingBusiness` på startsidan och kontaktsidan (alla språk): namn, `legalName` (GEG Gammeleksgården AB, från sidfoten), adress, telefon, e-post, koordinater, in- och utcheckning 17/11, 20 rum,
     `priceRange` "Från 795 kr", bekvämligheter, sociala länkar och Booking.
     **Borttaget eftersom det inte står på sajten:** pris 1895 kr, betalsätt (kort/Swish/faktura) och språk (`availableLanguage`).
   - `HotelRoom` + `Offer` (från 795 kr) på rumssidorna, `ItemList` på rumsöversikten, `EventVenue` för festlokalen, `Campground`/`RVPark` för ställplatsen,
     `SportsActivityLocation`/`TouristAttraction` för minigolfen, `Service` för företag, `FAQPage`, `TouristTrip` (Ven) och `ImageGallery`.
     Ingen `Restaurant`, eftersom ingen mat serveras. Inga betyg eller recensioner.
   - Minigolf: `isAccessibleForFree`/`publicAccess` borttagna. Texten säger "gratis för gäster" och "öppen för alla under säsong", så fälten stämde inte.
   - `BreadcrumbList` på alla undersidor. Rättat: brödsmulor, rumslistor och erbjudanden på andra språk pekade på svenska sidor och pekar nu på samma språk.
     Rums-URL:er hade avslutande `/` som inte matchade canonical. `&amp;` i namn är avkodat.
   - `WebSite.inLanguage` listar alla tio språk (stod `sv-SE` även på t.ex. engelska startsidan).
   - `VideoObject` borttaget på rundtursidorna. Drönarfilmen finns nu som `assets/video/flyover.mp4` (se 16 nov nedan); VideoObject kan läggas tillbaka.
3. **Sitemap och robots (inaktiva):** `lansering/sitemap.xml` (190 adresser, 19 sidor × 10 språk, med hreflang och x-default) och `lansering/robots.txt` med `Sitemap:`-rad.
   Bokningsvillkor, integritet, 404 och exempelsidan är utelämnade ur sitemap. Rot-`robots.txt` spärrar `/lansering/`.
   Ny sitemap: `python3 verktyg/seo.py sitemap > lansering/sitemap.xml`.
4. **Omdirigeringar från geghotel.se:** `lansering/omdirigeringar-geghotel.csv` (gammal adress → ny adress, 301).
   Repot har fem kända gamla adresser i `_redirects`: `/langtidsboende/`, `/evenemang/`, `/bokningsvillkor-2/`, `/en/long-term-stay/` och `/en/events/`. Alla är inlagda.
   De två engelska går nu till de engelska sidorna (`/en/...`), även i `_redirects`. Sista raden är en mall.
   **Fler gamla adresser behövs:** Daniel hämtar Search Console-data för geghotel.se (Sidor + Länkar, 16 månader) efter kontakt med ägaren.
   Lägg in en rad per adress som har klick, visningar eller externa länkar. Skicka bara till startsidan om det verkligen saknas en motsvarande sida, eftersom Google behandlar massomdirigeringar till startsidan som soft 404.
   OBS: `_redirects` och `_headers` används inte av GitHub Pages. Omdirigeringarna måste ligga på servern som svarar för **geghotel.se**, alltså gamla webbhotellet eller en DNS-/Cloudflare-regel. Exempel för Apache (.htaccess på geghotel.se):
   ```
   RewriteEngine On
   RewriteRule ^langtidsboende/?$ https://xn--gammeleksgrden-uib.se/foretag/langtidsboende [R=301,L]
   RewriteRule ^evenemang/?$ https://xn--gammeleksgrden-uib.se/fest-och-event/ [R=301,L]
   RewriteRule ^bokningsvillkor-2/?$ https://xn--gammeleksgrden-uib.se/bokningsvillkor/ [R=301,L]
   RewriteRule ^en/long-term-stay/?$ https://xn--gammeleksgrden-uib.se/en/foretag/langtidsboende [R=301,L]
   RewriteRule ^en/events/?$ https://xn--gammeleksgrden-uib.se/en/fest-och-event/ [R=301,L]
   RewriteRule ^ https://xn--gammeleksgrden-uib.se/ [R=301,L]
   ```
5. **IDN, alltså å i domänen:** alla maskinläsbara adresser skrivs i punycode `xn--gammeleksgrden-uib.se`: canonical, hreflang, og:url, JSON-LD, sitemap och robots.
   Skälen: `CNAME` för GitHub Pages är redan punycode, så samma värdnamn används överallt. Sitemap-protokollet och URL-standarden kräver ASCII i värdnamnet.
   Google behandlar formerna som samma domän och visar ändå `gammeleksgården.se` med å i sökresultaten. Synlig text och e-postadressen `kontakt@gammeleksgården.se` skrivs med å, eftersom de är till för människor.
   I Search Console: lägg till en **domänegenskap** för `gammeleksgården.se` (Google gör om den till punycode) och verifiera med DNS-TXT.
6. **Verktyg:** `verktyg/seo.py kontroll` kontrollerar title, description, H1, canonical, ömsesidig hreflang, alt, JSON-LD (giltig, rätt språk, befintliga sidor), brödsmulor och noindex.
   Med `--lanserad` kontrolleras i stället att noindex är borta, utom på 404 och exempelsidan.

Testat: `python3 verktyg/seo.py kontroll` → "Inga fel" (212 sidor). All JSON-LD går att tolka. Sitemap är giltig XML och har samma 190 adresser som tidigare.
Lanseringsstegen nedan är provkörda i en kopia av repot, och `kontroll --lanserad` gav "Inga fel".

## Gjort 16 nov 2026 (efter juryjämförelsen med geghotel.se)

Rapport och mätdata: projektmappen `geg-hotel/teknisk-jamforelse/`.

- **Startsidans film:** `hero-1080.mp4` (8,3 MB) ersatt av `hero-1280.mp4` (1,7 MB) och `hero-720.mp4` (0,7 MB), H.264 utan ljud. En WebP-stillbild (`hero-poster-720/1280.webp`, 50/129 kB) visas först och är LCP-elementet. Filmen hämtas först efter `load`, och inte alls vid "minska rörelse" eller sparat dataläge. Synlig pausknapp (WCAG 2.2.2).
- **Kontrast:** den mörka tonen (`.hero-film::before`) ligger nu ovanpå filmen (z-index). Boka-knappen i menyn har mörk text, länkar i topplisten är understrukna, fokusringen är mörk mässing på ljus botten.
- **Typsnitt på egen server:** `css/fonts.css` + `assets/fonts/*.woff2` (OFL), `font-display: optional` och preload. Inga anrop till Google.
- **Säkerhet:** meta-CSP och referrer-policy i alla 212 sidor (GitHub Pages kan inte skicka rubriker). `_headers` har nu CSP med `frame-ancestors 'none'` och X-Frame-Options för Cloudflare Pages. Ändras formulärtjänsten från Formspree måste CSP:n (connect-src, form-action) ändras på alla sidor.
- **Omdömen:** källa och datum under betygen (Hotels.com, 150 omdömen, okt 2026) och tydligt att texterna är sammanfattningar.
- **Innehåll från geghotel.se** (alla tio språk): fest (dansgolv, egen musik, terrass/gård, tillgänglighet, egen mat och dryck eller catering), långtidsboende (arbetsfordon, laddning, smart-TV, samlad faktura, konferensrum) och Upptäck (golf, Sandbergen/Skåneleden, Borgen/Glumslöv, kanot/kajak/SUP, Väla).
- **Övrigt:** WhatsApp-länk (wa.me) i topplisten, Esc stänger menyn, inga sidledsglidningar vid 320 px på 100 testade sidor, rubrikordning, landmärken (`aside`) för topplist och förhandsremsa, 404-sidans språklänkar, avstånden på startsidan.
- **Omdirigeringar:** `_redirects` och `lansering/omdirigeringar-geghotel.csv` följer nu geghotel.se:s verkliga sitemap (13 sidor) plus policy- och kontaktlänkar. Exemplet för .htaccess ovan är äldre; använd CSV:n. Gäller oavsett namnval: behålls namnet GEG Hotel och sajten läggs på geghotel.se behövs samma sökvägar.
- Testat: `verktyg/seo.py kontroll` "Inga fel" (212 sidor), axe 0 fel på 17 sidor i ljust och mörkt läge, Lighthouse lokalt startsidan mobil 74 → 96 (LCP 5,6 → 2,7 s).

## Gjort 17 nov 2026 (360°-bilderna inbyggda)

- **Visare:** Pannellum 2.5.6 (MIT) på egen server i `assets/pano/` (licens bredvid). Inget hämtas förrän besökaren klickar på "Gå runt i 360°"; sidan visar en vanlig stillbild (`assets/img/pano-<id>-800/1600`) tills dess. Bilderna finns i två storlekar, `<id>-2048.jpg` (mobil) och `<id>-4096.jpg` (stora skärmar med stöd för det). Bara en visning är igång åt gången. Pilar mellan vyerna och startvinklar ligger i `js/main.js` (LINKS), samma som i rundturen från fotograferingen.
- **Var:** startsidan (gården), rumsöversikten (ny sektion `#rumstyper` med de fyra sängupplägg, rum 10/9/7/6, ritning nere/loft och en visning per typ), varje rumssida (rum, loft, badrum), fest (festlokalen), bröllop, företag (rum 6), långtidsboende (gästköket), minigolf och rundtursidan (hela gården, alla vyer). Drönarstillbilder (`fran-luften-*`) på Upptäck, i galleriet och på rundtursidan.
- **Texter:** `verktyg/rundturer_text.py` (alla tio språk, maskinöversatta). Bygget: `python3 verktyg/rundturer.py` hoppar över sidor som redan har en visning. Varje sida får `<script id="pano-t">` med sina scentexter.
- **CSP:** `img-src` har nu `blob:` (Pannellum laddar bilden som blob) i alla sidor och i `_headers`.
- **Rättat på köpet:** rumssidornas bokningsruta låg i två kolumner även på mobil (inline-stil vann över mediefrågan), så texten i vänsterspalten blev 0 px bred. Nu en spalt under 900 px.
- 360°-materialet är bara för webbplatsen, aldrig för Google. Den dukade 360°-bilden av stora salen finns inte med (den låg bara på Daniels Mac); läggs in som märkt illustration om den ska med.
- Testat: `verktyg/seo.py kontroll` "Inga fel" (212 sidor). Lighthouse lokalt mobil: startsidan 96, rum 96, fest 97, rumssida 98; tillgänglighet 100. Inga CSP- eller skriptfel när visningarna startas på sv, en, de, fr, it, nb, fi.

## Lanseringschecklista (upprättad 26 okt 2026)

Gör ingenting av detta förrän ägaren av GammelEksGården sagt ja.

1. [ ] Skriftligt ja från ägaren. Toto/Peter godkänner priser och uppgifter.
2. [ ] Search Console-data för geghotel.se hämtad. `lansering/omdirigeringar-geghotel.csv` ifylld och mallraden borttagen.
3. [ ] Ta bort förhandsremsan "Förhandsversion …" (`<div class="proto">`) på alla sidor.
4. [ ] Ta bort noindex (utom 404 och exempelsidan), i generatorn om den finns, annars:
   `grep -rl --include='*.html' '<meta name="robots" content="noindex, follow">' . | grep -v -e '^\./404\.html$' -e '^\./exempel/' -e '^\./\.git/' | xargs sed -i '/<meta name="robots" content="noindex, follow">/d'`
5. [ ] `python3 verktyg/seo.py sitemap > sitemap.xml` (ger dagens lastmod) och `cp lansering/robots.txt robots.txt`.
6. [ ] `python3 verktyg/seo.py kontroll --lanserad` → "Inga fel". Gör en PR och låt Daniel granska och slå ihop.
7. [ ] Kontrollera live: `https://xn--gammeleksgrden-uib.se/robots.txt` och `/sitemap.xml` svarar, och sidkällan saknar noindex.
8. [ ] Search Console: domänegenskap för gammeleksgården.se (DNS-TXT). Skicka in sitemap och begär indexering av startsidan.
9. [ ] Aktivera 301-omdirigeringarna på geghotel.se samma dag. Testa varje rad i CSV:n med `curl -I`.
10. [ ] Search Console för geghotel.se: Ändring av adress → gammeleksgården.se.
11. [ ] Uppdatera webbadressen i Google Företagsprofil, Booking.com, Instagram och Facebook till gammeleksgården.se.
12. [ ] Låt omdirigeringarna och geghotel.se-domänen ligga kvar i minst ett år. Följ täckning och 404-fel i Search Console de första veckorna.

## Nästa steg och kända brister (utanför detta uppdrag)

- ~~Drönarfilmen saknas~~ Finns sedan 16 nov som `assets/video/flyover.mp4` (3,6 MB).
  Lägg in filen (eller peka om till `assets/video/`) och lägg tillbaka `VideoObject` med rätt `contentUrl` och verkligt uppladdningsdatum.
- ~~360°-rundturen är en platshållare~~ Inbyggd 17 nov.
- Besöksstatistik: bara Fathom (site CBINBQJR). GoatCounter är borttaget från alla sidor och integritetssidorna nämner Fathom (16 nov 2026).
- 404-sidans språkväljare länkar till `en/404` och så vidare, adresser som inte finns. Påverkar inte SEO (sidan har noindex) men bör rättas i generatorn.
- 136 title är längre än cirka 60 tecken och kan kortas i sökresultaten. De är unika och lämnade orörda. Korta dem gärna i generatorn, till exempel genom att ta bort " | Gammeleksgården" på undersidor.
- Koordinaterna 55.922, 12.844 har tre decimaler. Stäm av mot Google Maps-pinnen vid lansering.
- I `HotelRoom` på andra språk är fälten `bed` och `unitText` fortfarande på svenska. Det påverkar inte rich results men kan översättas i generatorn.
