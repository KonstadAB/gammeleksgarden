# HANDOFF – gammeleksgården.se

Senast uppdaterad: 26 okt 2026 (HQ uppdrag #6, gren `hq/seo-forberedelse-for-gammeleksgarden-se--2610261121`).

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
   - `VideoObject` borttaget på rundtursidorna: filen `assets/img/flyover.mp4` finns inte i repot (se nästa steg).
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

- **Drönarfilmen saknas:** startsidan och rundtursidan (alla språk) visar en videospelare med `assets/img/flyover.mp4`, men filen finns inte i repot.
  Lägg in filen (eller peka om till `assets/video/`) och lägg tillbaka `VideoObject` med rätt `contentUrl` och verkligt uppladdningsdatum.
- 360°-rundturen är en platshållare ("bäddas in efter fotograferingen"), medan rundturens meta-text lovar 360°. Byt texten eller lägg in rundturen före lansering.
- Integritetssidan nämner bara GoatCounter, men Fathom finns också på alla sidor sedan PR #1. Texten behöver beslut från Daniel.
- 404-sidans språkväljare länkar till `en/404` och så vidare, adresser som inte finns. Påverkar inte SEO (sidan har noindex) men bör rättas i generatorn.
- 136 title är längre än cirka 60 tecken och kan kortas i sökresultaten. De är unika och lämnade orörda. Korta dem gärna i generatorn, till exempel genom att ta bort " | Gammeleksgården" på undersidor.
- Koordinaterna 55.922, 12.844 har tre decimaler. Stäm av mot Google Maps-pinnen vid lansering.
- I `HotelRoom` på andra språk är fälten `bed` och `unitText` fortfarande på svenska. Det påverkar inte rich results men kan översättas i generatorn.
