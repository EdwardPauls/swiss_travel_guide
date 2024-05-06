from flask_babel import _

class SuggestionCard:
  def __init__(self, title: str, link_text: str, query: str, img: str):
    self.title: str = title
    self.link_text: str = link_text
    self.query: str = query
    self.img: str = img

LINK_TEXT = _('Try it')
SUGGESTION_CARDS = {
    'Zurich': [
        SuggestionCard(
            title=_('Beach holidays for a family in Europe'),
            link_text=LINK_TEXT,
            query=
                _('We are a family of three and we are looking for a beach holiday in Europe for the next summer. What are good destinations where we can also enjoy some cultural activities?')
            ,
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/efl-square.jpg',
        ),
        SuggestionCard(
            title=_('Asian food with friends'),
            link_text=LINK_TEXT,
            query=
                _('I want to explore Asian culture and food in a metropolitan destination with my friends. Any trendy destination you can suggest and with a nice itinerary?')
            ,
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/sgn-square.jpg',
        ),
        SuggestionCard(
            title=_('Surf trip in South America'),
            link_text=LINK_TEXT,
            query=
                _('I would like to travel to South America with my friends. We like surfing but also love to enjoy the local food. Do you have good suggestions?')
            ,
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/baq-square.jpg',
        ),
    ],
 'Geneva': [
        SuggestionCard(
            title=_('Beach holidays for a family in Europe'),
            link_text=LINK_TEXT,
            query=_('We are a family of three and we are looking for a beach holiday in Europe for the next summer. What are good destinations where we can also enjoy some cultural activities?'),
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/efl-square.jpg',
        ),
        SuggestionCard(
            title=_('Gateway to the Nordics'),
            link_text=LINK_TEXT,
            query=
                _('I want to visit Stockholm with my boyfriend for a few days. What kind of activities can we do there ? Can you share an itinerary for our stay?')
            ,
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/got-square.jpg',
        ),
        SuggestionCard(
            title=_('Shopping in the U.S.'),
            link_text=LINK_TEXT,
            query=
                _("I want to go shopping in a big city in the US. I also like some cultural activities when I am around. Do you have any suggestions?")
            ,
            img='https://www.swiss.com/content/dam/lx/images/offers/destination/nyc-square.jpg',
        ),
    ]
}
