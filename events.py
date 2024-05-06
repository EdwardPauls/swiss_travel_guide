from typing import Optional, List
import logging
import json
import datetime

class Event:

  def __init__(self, event_title, country_code, city_code, event_start_dt, event_end_dt, classification_type):
    self.event_title: str = event_title
    self.country_code: str = country_code
    self.city_code: str = city_code
    self.event_start_dt: str = event_start_dt
    self.event_end_dt: str = event_end_dt
    self.classification_type: str = classification_type

  def summary(self):
    return {
        "event title": self.event_title,
        "event start date": self.event_start_dt,
        "event end date": self.event_end_dt,
        "type of event": self.classification_type
        }

ALL_EVENTS = [
Event(
      event_title="Light + Building Frankfurt",
      country_code="de",
      city_code="fra",
      event_start_dt="03.03.2024",
      event_end_dt="08.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="GiveADays",
      country_code="de",
      city_code="str",
      event_start_dt="13.02.2025",
      event_end_dt="15.02.2025",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ESCRS Congress & Exhibition",
      country_code="es",
      city_code="bcn",
      event_start_dt="06.09.2024",
      event_end_dt="10.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Bridal Week",
      country_code="de",
      city_code="dus",
      event_start_dt="13.04.2024",
      event_end_dt="15.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Marche Du Film",
      country_code="fr",
      city_code="nce",
      event_start_dt="14.05.2024",
      event_end_dt="25.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="INTERNORGA - Leitmesse f�r den Au�er-Haus-Markt",
      country_code="de",
      city_code="ham",
      event_start_dt="08.03.2024",
      event_end_dt="12.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Marathon Lima 42K",
      country_code="pe",
      city_code="lim",
      event_start_dt="19.05.2024",
      event_end_dt="19.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="CPhl worldwide Pharmakongress",
      country_code="it",
      city_code="mil",
      event_start_dt="08.10.2024",
      event_end_dt="10.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Altenpflege",
      country_code="de",
      city_code="haj",
      event_start_dt="23.04.2024",
      event_end_dt="25.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="PITTI FILATI Summer",
      country_code="it",
      city_code="flr",
      event_start_dt="26.06.2024",
      event_end_dt="28.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Australia",
      country_code="au",
      city_code="mel",
      event_start_dt="24.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Chillventa",
      country_code="de",
      city_code="nue",
      event_start_dt="08.10.2024",
      event_end_dt="10.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Sensor+Test",
      country_code="de",
      city_code="nue",
      event_start_dt="11.06.2024",
      event_end_dt="13.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="PCIM Europe",
      country_code="de",
      city_code="nue",
      event_start_dt="11.06.2024",
      event_end_dt="13.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="str",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Formula 1 Grand Prix Mexico",
      country_code="mx",
      city_code="mex",
      event_start_dt="27.10.2024",
      event_end_dt="27.10.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="FIFA Futsal World Cup",
      country_code="lt",
      city_code="vno",
      event_start_dt="06.09.2024",
      event_end_dt="05.10.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="OutDoor - Europ�ische Outdoor-Fachmesse",
      country_code="de",
      city_code="muc",
      event_start_dt="03.06.2024",
      event_end_dt="05.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="SMTconnect",
      country_code="de",
      city_code="nue",
      event_start_dt="11.06.2024",
      event_end_dt="13.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Cosmoprof / Cosmopack",
      country_code="it",
      city_code="blq",
      event_start_dt="21.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="fra",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Eishockey-WM",
      country_code="cz",
      city_code="prg",
      event_start_dt="10.05.2024",
      event_end_dt="26.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="infa - Erlebnis-und Einkaufsmesse",
      country_code="de",
      city_code="haj",
      event_start_dt="12.10.2024",
      event_end_dt="20.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Electronica",
      country_code="de",
      city_code="muc",
      event_start_dt="12.11.2024",
      event_end_dt="15.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="IAW",
      country_code="de",
      city_code="cgn",
      event_start_dt="04.03.2024",
      event_end_dt="06.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="MIPIM Salon international de l'immobilier",
      country_code="fr",
      city_code="nce",
      event_start_dt="11.03.2024",
      event_end_dt="15.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Deutscher Katholikentag",
      country_code="de",
      city_code="drs",
      event_start_dt="29.05.2024",
      event_end_dt="02.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="EXPO REAL",
      country_code="de",
      city_code="muc",
      event_start_dt="07.10.2024",
      event_end_dt="09.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="UEFA Europa Conference League",
      country_code="gr",
      city_code="ath",
      event_start_dt="29.05.2024",
      event_end_dt="29.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="GTM",
      country_code="de",
      city_code="drs",
      event_start_dt="21.04.2024",
      event_end_dt="23.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="LAHTI - Skiing and Skijumping World Cup",
      country_code="fi",
      city_code="hel",
      event_start_dt="01.03.2024",
      event_end_dt="03.03.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="BAU",
      country_code="de",
      city_code="muc",
      event_start_dt="13.01.2025",
      event_end_dt="18.01.2025",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix China",
      country_code="cn",
      city_code="sha",
      event_start_dt="21.04.2024",
      event_end_dt="21.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Prolight + Sound",
      country_code="de",
      city_code="fra",
      event_start_dt="19.03.2024",
      event_end_dt="22.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Mostra del Cinema",
      country_code="it",
      city_code="vce",
      event_start_dt="28.08.2024",
      event_end_dt="07.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="HOMI Fashion & Jewels Exhibition Summer",
      country_code="it",
      city_code="mil",
      event_start_dt="13.09.2024",
      event_end_dt="16.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="World Athletics Indoor Championships",
      country_code="gb",
      city_code="gla",
      event_start_dt="01.03.2024",
      event_end_dt="03.03.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="FCE Cosmetique",
      country_code="br",
      city_code="sao",
      event_start_dt="04.06.2024",
      event_end_dt="06.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Beauty International",
      country_code="de",
      city_code="dus",
      event_start_dt="22.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Genfer Autosalon",
      country_code="ch",
      city_code="gva",
      event_start_dt="26.02.2024",
      event_end_dt="03.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Future AAN Annual Meetings",
      country_code="us",
      city_code="den",
      event_start_dt="13.04.2024",
      event_end_dt="19.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Cevisama",
      country_code="es",
      city_code="vlc",
      event_start_dt="26.02.2024",
      event_end_dt="01.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Milan Fashion Week Men's Spring/Summer",
      country_code="it",
      city_code="mil",
      event_start_dt="15.06.2024",
      event_end_dt="19.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="INTERNATIONALE EISENWARENMESSE K�LN ",
      country_code="de",
      city_code="cgn",
      event_start_dt="03.03.2024",
      event_end_dt="06.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Wire und Tube DUS",
      country_code="de",
      city_code="dus",
      event_start_dt="15.04.2024",
      event_end_dt="19.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Japan",
      country_code="jp",
      city_code="ngo",
      event_start_dt="07.04.2024",
      event_end_dt="07.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Routes Europe",
      country_code="dk",
      city_code="aar",
      event_start_dt="22.04.2024",
      event_end_dt="24.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Canada",
      country_code="ca",
      city_code="ymq",
      event_start_dt="09.06.2024",
      event_end_dt="09.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Milan Fashion Week Women's Fall/Winter",
      country_code="it",
      city_code="mil",
      event_start_dt="20.02.2024",
      event_end_dt="26.02.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="SANA",
      country_code="it",
      city_code="blq",
      event_start_dt="05.09.2024",
      event_end_dt="08.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Cibus",
      country_code="it",
      city_code="blq",
      event_start_dt="07.05.2024",
      event_end_dt="10.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="dus",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Interzoo",
      country_code="de",
      city_code="nue",
      event_start_dt="07.05.2024",
      event_end_dt="10.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Singapore",
      country_code="sg",
      city_code="sin",
      event_start_dt="22.09.2024",
      event_end_dt="22.09.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Balttechnika-Intern technologies.innovations",
      country_code="lt",
      city_code="vno",
      event_start_dt="15.05.2024",
      event_end_dt="17.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Rio Oil & Gas Expo",
      country_code="br",
      city_code="rio",
      event_start_dt="23.09.2024",
      event_end_dt="25.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Reise und Camping",
      country_code="de",
      city_code="dus",
      event_start_dt="28.02.2024",
      event_end_dt="03.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Comic Con",
      country_code="us",
      city_code="san",
      event_start_dt="25.07.2024",
      event_end_dt="28.07.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Embedded World",
      country_code="de",
      city_code="nue",
      event_start_dt="09.04.2024",
      event_end_dt="11.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="DRUPA",
      country_code="de",
      city_code="dus",
      event_start_dt="28.05.2024",
      event_end_dt="07.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="MICAM / MIPEL International Footwear Fall",
      country_code="it",
      city_code="mil",
      event_start_dt="15.09.2024",
      event_end_dt="18.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="analytica",
      country_code="de",
      city_code="muc",
      event_start_dt="09.04.2024",
      event_end_dt="12.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Techtextil",
      country_code="de",
      city_code="fra",
      event_start_dt="23.04.2024",
      event_end_dt="26.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="fish international",
      country_code="de",
      city_code="bre",
      event_start_dt="25.02.2024",
      event_end_dt="27.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Marat�n de Mendoza",
      country_code="ar",
      city_code="mdz",
      event_start_dt="28.04.2024",
      event_end_dt="28.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Singapore Airshow",
      country_code="sg",
      city_code="sin",
      event_start_dt="20.02.2024",
      event_end_dt="25.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="CAKE & BAKE",
      country_code="de",
      city_code="dus",
      event_start_dt="23.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Miami",
      country_code="us",
      city_code="mia",
      event_start_dt="05.05.2024",
      event_end_dt="05.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Eid al-Adha",
      country_code="az",
      city_code="bak",
      event_start_dt="14.06.2024",
      event_end_dt="16.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="World Athletics U20 Championships",
      country_code="pe",
      city_code="lim",
      event_start_dt="26.08.2024",
      event_end_dt="31.08.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Formula 1 Grand Prix Azerbaijan",
      country_code="az",
      city_code="bak",
      event_start_dt="15.09.2024",
      event_end_dt="15.09.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="MIPDOC (internat. showcase for documentary screen.)",
      country_code="fr",
      city_code="nce",
      event_start_dt="15.04.2024",
      event_end_dt="17.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula E - Rome",
      country_code="it",
      city_code="rom",
      event_start_dt="13.04.2024",
      event_end_dt="14.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="World Water Week",
      country_code="se",
      city_code="sto",
      event_start_dt="23.08.2024",
      event_end_dt="27.08.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Hajj",
      country_code="sa",
      city_code="jed",
      event_start_dt="14.06.2024",
      event_end_dt="19.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="ISS World - Dubai",
      country_code="ae",
      city_code="dxb",
      event_start_dt="05.03.2024",
      event_end_dt="07.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="EIMA",
      country_code="it",
      city_code="blq",
      event_start_dt="06.11.2024",
      event_end_dt="10.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Hungary",
      country_code="hu",
      city_code="bud",
      event_start_dt="21.07.2024",
      event_end_dt="21.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="EnergyDecentral",
      country_code="de",
      city_code="haj",
      event_start_dt="12.11.2024",
      event_end_dt="15.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="New York International Auto Show",
      country_code="us",
      city_code="nyc",
      event_start_dt="29.03.2024",
      event_end_dt="07.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="SEAFOOD EXPO",
      country_code="es",
      city_code="bcn",
      event_start_dt="23.04.2024",
      event_end_dt="25.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title=" 	Formula 1 Grand Prix United States - LAS",
      country_code="us",
      city_code="las",
      event_start_dt="23.11.2024",
      event_end_dt="23.11.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Pest-Protect",
      country_code="de",
      city_code="fra",
      event_start_dt="13.11.2024",
      event_end_dt="14.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="didacta - die Bildungsmesse",
      country_code="de",
      city_code="cgn",
      event_start_dt="20.02.2024",
      event_end_dt="24.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="LINEAPELLE FAIR Fall",
      country_code="it",
      city_code="mil",
      event_start_dt="17.09.2024",
      event_end_dt="19.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Imola",
      country_code="it",
      city_code="blq",
      event_start_dt="19.05.2024",
      event_end_dt="19.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Intersolar",
      country_code="de",
      city_code="muc",
      event_start_dt="19.06.2024",
      event_end_dt="21.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="fensterbau frontale",
      country_code="de",
      city_code="nue",
      event_start_dt="19.03.2024",
      event_end_dt="22.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="IAA Nutzfahrzeuge",
      country_code="de",
      city_code="haj",
      event_start_dt="17.09.2024",
      event_end_dt="22.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Helsinki CUP junior football tournament",
      country_code="fi",
      city_code="hel",
      event_start_dt="08.07.2024",
      event_end_dt="13.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="ColombiaPlast",
      country_code="co",
      city_code="bog",
      event_start_dt="30.09.2024",
      event_end_dt="04.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Cannes Lions International Festival of Creativity (formerly Cannes Lions Int'l Adverstising Festival)",
      country_code="fr",
      city_code="nce",
      event_start_dt="17.06.2024",
      event_end_dt="21.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="New York Fashion Week Spring / Summer",
      country_code="us",
      city_code="nyc",
      event_start_dt="10.10.2024",
      event_end_dt="12.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="ham",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="cgn",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="EUROBIKE Internationale Fahrradmesse",
      country_code="de",
      city_code="fra",
      event_start_dt="03.07.2024",
      event_end_dt="07.07.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="METAV",
      country_code="de",
      city_code="dus",
      event_start_dt="20.02.2024",
      event_end_dt="23.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Porto Alegre Marathon",
      country_code="br",
      city_code="poa",
      event_start_dt="15.06.2024",
      event_end_dt="16.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Top Hair",
      country_code="de",
      city_code="dus",
      event_start_dt="23.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Austria",
      country_code="at",
      city_code="grz",
      event_start_dt="30.06.2024",
      event_end_dt="30.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Medical Fair Asia",
      country_code="sg",
      city_code="sin",
      event_start_dt="11.09.2024",
      event_end_dt="13.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="GSM - MWC (Mobile World Congress)",
      country_code="es",
      city_code="bcn",
      event_start_dt="26.02.2024",
      event_end_dt="29.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Salone Nautico Venezia",
      country_code="it",
      city_code="vce",
      event_start_dt="29.05.2024",
      event_end_dt="02.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ProWein",
      country_code="de",
      city_code="dus",
      event_start_dt="10.03.2024",
      event_end_dt="12.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Great Britain - Silverstone",
      country_code="gb",
      city_code="bhx",
      event_start_dt="07.07.2024",
      event_end_dt="07.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Umrah Season",
      country_code="sa",
      city_code="jed",
      event_start_dt="15.03.2024",
      event_end_dt="10.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="GLASSTEC Int. Fair for Glass Production",
      country_code="de",
      city_code="dus",
      event_start_dt="22.10.2024",
      event_end_dt="25.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Enforce Tac",
      country_code="de",
      city_code="nue",
      event_start_dt="26.02.2024",
      event_end_dt="28.02.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="WTM Latin America",
      country_code="br",
      city_code="sao",
      event_start_dt="02.04.2024",
      event_end_dt="04.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="EMV",
      country_code="de",
      city_code="cgn",
      event_start_dt="12.03.2024",
      event_end_dt="14.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ORGATEC",
      country_code="de",
      city_code="cgn",
      event_start_dt="22.10.2024",
      event_end_dt="26.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="EAGE Annual",
      country_code="no",
      city_code="osl",
      event_start_dt="10.06.2024",
      event_end_dt="14.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Salone del Mobile - furniture saloon",
      country_code="it",
      city_code="mil",
      event_start_dt="16.04.2024",
      event_end_dt="21.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="FachpackPrintpack/Logintern",
      country_code="de",
      city_code="nue",
      event_start_dt="24.09.2024",
      event_end_dt="26.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="AERO Int. Fachmesse f�r allgemeine Luftfahrt",
      country_code="de",
      city_code="fdh",
      event_start_dt="17.04.2024",
      event_end_dt="20.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="PITTI UOMO Summer",
      country_code="it",
      city_code="flr",
      event_start_dt="11.06.2024",
      event_end_dt="14.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="EuroTier",
      country_code="de",
      city_code="haj",
      event_start_dt="12.11.2024",
      event_end_dt="15.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ART D�sseldorf",
      country_code="de",
      city_code="dus",
      event_start_dt="12.04.2024",
      event_end_dt="14.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="AACAP's Annual Meeting",
      country_code="us",
      city_code="sea",
      event_start_dt="14.10.2024",
      event_end_dt="19.10.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="IATA Annual Gerneral Meeting (AGM)",
      country_code="ae",
      city_code="dxb",
      event_start_dt="02.06.2024",
      event_end_dt="04.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="ALUMINIUM",
      country_code="de",
      city_code="dus",
      event_start_dt="08.10.2024",
      event_end_dt="10.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Floripa International Marathon",
      country_code="br",
      city_code="fln",
      event_start_dt="02.06.2024",
      event_end_dt="02.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="gamescom (Europ. trade fair for interactive games)",
      country_code="de",
      city_code="cgn",
      event_start_dt="21.08.2024",
      event_end_dt="25.08.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="MODA Made in Italy",
      country_code="de",
      city_code="muc",
      event_start_dt="25.03.2024",
      event_end_dt="27.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="US OPEN",
      country_code="us",
      city_code="nyc",
      event_start_dt="26.08.2024",
      event_end_dt="08.09.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Achema Frankfurt",
      country_code="de",
      city_code="fra",
      event_start_dt="10.06.2024",
      event_end_dt="14.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="IAAPA Conference & EXPO Europe - Euro Attractions Show",
      country_code="nl",
      city_code="ams",
      event_start_dt="23.09.2024",
      event_end_dt="26.09.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Automechanika",
      country_code="de",
      city_code="fra",
      event_start_dt="10.09.2024",
      event_end_dt="14.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="SurfaceTechnology GERMANY",
      country_code="de",
      city_code="str",
      event_start_dt="04.06.2024",
      event_end_dt="06.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ICU World Championships Cheerleading",
      country_code="us",
      city_code="orl",
      event_start_dt="26.04.2024",
      event_end_dt="29.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="tire technology EXPO",
      country_code="de",
      city_code="haj",
      event_start_dt="19.03.2024",
      event_end_dt="21.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Deloitte Seamless Cards & Payments Middle East",
      country_code="ae",
      city_code="dxb",
      event_start_dt="14.05.2024",
      event_end_dt="15.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Internationale Handwerksmesse",
      country_code="de",
      city_code="muc",
      event_start_dt="28.02.2024",
      event_end_dt="03.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Aqua-Fish",
      country_code="de",
      city_code="fdh",
      event_start_dt="08.03.2024",
      event_end_dt="10.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Italy - Monza",
      country_code="it",
      city_code="mil",
      event_start_dt="01.09.2024",
      event_end_dt="01.09.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="UEFA Champions League Final",
      country_code="gb",
      city_code="lon",
      event_start_dt="01.06.2024",
      event_end_dt="01.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Automechanika Buenos Aires",
      country_code="ar",
      city_code="bue",
      event_start_dt="10.04.2024",
      event_end_dt="13.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="EuroBLECH",
      country_code="de",
      city_code="haj",
      event_start_dt="22.10.2024",
      event_end_dt="25.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Partille Cup",
      country_code="se",
      city_code="got",
      event_start_dt="01.07.2024",
      event_end_dt="06.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Hannovermesse",
      country_code="de",
      city_code="haj",
      event_start_dt="22.04.2024",
      event_end_dt="26.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="FIBO -  Internationale Leitmesse f�r Fitness. Wellness und Gesundheit",
      country_code="de",
      city_code="cgn",
      event_start_dt="11.04.2024",
      event_end_dt="14.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Spain",
      country_code="es",
      city_code="bcn",
      event_start_dt="23.06.2024",
      event_end_dt="23.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Anime Japan",
      country_code="jp",
      city_code="tyo",
      event_start_dt="23.03.2024",
      event_end_dt="24.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="IFAT ENTSORGA",
      country_code="de",
      city_code="muc",
      event_start_dt="13.05.2024",
      event_end_dt="17.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Milan Fashion Week Women's Fall/Winter",
      country_code="it",
      city_code="mil",
      event_start_dt="19.02.2025",
      event_end_dt="25.02.2025",
      classification_type="Special Event"
    ),
Event(
      event_title="Childern's Book Fair",
      country_code="it",
      city_code="blq",
      event_start_dt="08.04.2024",
      event_end_dt="11.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="European Football Championship",
      country_code="de",
      city_code="muc",
      event_start_dt="14.06.2024",
      event_end_dt="14.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Formula 1 Grand Prix United States - AUS",
      country_code="us",
      city_code="aus",
      event_start_dt="20.10.2024",
      event_end_dt="20.10.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Expo Agrofuturo",
      country_code="co",
      city_code="bog",
      event_start_dt="23.10.2024",
      event_end_dt="25.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Frankfurter Buchmesse",
      country_code="de",
      city_code="fra",
      event_start_dt="16.10.2024",
      event_end_dt="20.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Scanpack",
      country_code="se",
      city_code="got",
      event_start_dt="22.10.2024",
      event_end_dt="25.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Anutec International Foodtec India. Mumbai",
      country_code="in",
      city_code="bom",
      event_start_dt="22.10.2024",
      event_end_dt="24.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Dutch",
      country_code="nl",
      city_code="ams",
      event_start_dt="25.08.2024",
      event_end_dt="25.08.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Summer Olympics",
      country_code="fr",
      city_code="par",
      event_start_dt="26.07.2024",
      event_end_dt="11.08.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="COSMETICA",
      country_code="de",
      city_code="fdh",
      event_start_dt="15.06.2024",
      event_end_dt="16.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Caspian Oil and Gas Exhibition",
      country_code="az",
      city_code="bak",
      event_start_dt="04.06.2024",
      event_end_dt="06.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Eid al-Fitr",
      country_code="az",
      city_code="bak",
      event_start_dt="08.04.2024",
      event_end_dt="09.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Oktoberfest MUC",
      country_code="de",
      city_code="muc",
      event_start_dt="21.09.2024",
      event_end_dt="06.10.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="PITTI BIMBO Summer",
      country_code="it",
      city_code="flr",
      event_start_dt="19.06.2024",
      event_end_dt="21.06.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Aircraft Interiors Expo",
      country_code="de",
      city_code="ham",
      event_start_dt="28.05.2024",
      event_end_dt="30.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="ANEX - Asia Nonwovens Exhibition",
      country_code="tw",
      city_code="tpe",
      event_start_dt="22.05.2024",
      event_end_dt="24.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Six Nations: Italy vs Scotland",
      country_code="it",
      city_code="rom",
      event_start_dt="08.03.2024",
      event_end_dt="10.03.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="BATIMAT",
      country_code="fr",
      city_code="par",
      event_start_dt="30.09.2024",
      event_end_dt="03.10.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Intermodal South America",
      country_code="br",
      city_code="sao",
      event_start_dt="05.03.2024",
      event_end_dt="07.03.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Wind Energy",
      country_code="de",
      city_code="ham",
      event_start_dt="24.09.2024",
      event_end_dt="27.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Texcare",
      country_code="de",
      city_code="fra",
      event_start_dt="09.11.2024",
      event_end_dt="13.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Japan",
      country_code="jp",
      city_code="osa",
      event_start_dt="07.04.2024",
      event_end_dt="07.04.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Formula E - New York",
      country_code="us",
      city_code="pdx",
      event_start_dt="29.06.2024",
      event_end_dt="29.06.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="NPE",
      country_code="us",
      city_code="orl",
      event_start_dt="06.05.2024",
      event_end_dt="10.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Great Britain - Silverstone",
      country_code="gb",
      city_code="lon",
      event_start_dt="07.07.2024",
      event_end_dt="07.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="MONACO YACHT SHOW",
      country_code="fr",
      city_code="nce",
      event_start_dt="25.09.2024",
      event_end_dt="28.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="World youth championship in ice hockey U-18",
      country_code="fi",
      city_code="hel",
      event_start_dt="25.04.2024",
      event_end_dt="05.05.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="Agrishow",
      country_code="br",
      city_code="sao",
      event_start_dt="29.04.2024",
      event_end_dt="03.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Bahrain",
      country_code="bh",
      city_code="bah",
      event_start_dt="02.03.2024",
      event_end_dt="02.03.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="INTERMODELLBAU",
      country_code="de",
      city_code="dus",
      event_start_dt="18.04.2024",
      event_end_dt="21.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Brazil",
      country_code="br",
      city_code="sao",
      event_start_dt="03.11.2024",
      event_end_dt="03.11.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="SMM Shipbuilding",
      country_code="de",
      city_code="ham",
      event_start_dt="03.09.2024",
      event_end_dt="06.09.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Gothia cup",
      country_code="se",
      city_code="got",
      event_start_dt="14.07.2024",
      event_end_dt="20.07.2024",
      classification_type="Special Event"
    ),
Event(
      event_title="MIPTV (world's adiovisiual & digital content m.)",
      country_code="fr",
      city_code="nce",
      event_start_dt="15.04.2024",
      event_end_dt="17.04.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Vitafoods Europe",
      country_code="ch",
      city_code="gva",
      event_start_dt="14.05.2024",
      event_end_dt="16.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title=" Venture Capital World Summit",
      country_code="us",
      city_code="nyc",
      event_start_dt="15.05.2024",
      event_end_dt="15.05.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="formnext",
      country_code="de",
      city_code="fra",
      event_start_dt="19.11.2024",
      event_end_dt="22.11.2024",
      classification_type="Fair/Exhibition"
    ),
Event(
      event_title="Formula 1 Grand Prix Monaco",
      country_code="fr",
      city_code="nce",
      event_start_dt="26.05.2024",
      event_end_dt="26.05.2024",
      classification_type="Special Event"
    )
]

def get_month(event_date: str):
  return datetime.datetime.strptime(event_date, '%d.%m.%Y').month

def mapped_month(month: int):
  current_month = datetime.date.today().month
  month = month if month >= current_month else month + 12
  return month

def get_events(city_code: Optional[str] = None, country_code: Optional[str] = None,
    city_code_exclusion: Optional[str] = None, start_month: Optional[int] = None,
    end_month: Optional[int] = None,
) -> List[str]:
  events = []
  for event in ALL_EVENTS:
    if city_code and event.city_code.lower() != city_code.lower():
      continue
    if country_code and event.country_code.lower() != country_code.lower():
      continue
    if city_code_exclusion and event.city_code.lower() == city_code_exclusion.lower():
      continue
    if start_month and end_month:
      start_month = mapped_month(start_month)
      end_month = mapped_month(end_month)
      event_start_month = mapped_month(get_month(event.event_start_dt))
      event_end_month = mapped_month(get_month(event.event_end_dt))

      if start_month > event_end_month or end_month < event_end_month:
        continue

    events.append(event.summary())
  return events

