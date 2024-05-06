EXAMPLES = """
--- EXAMPLES BEGIN ---

EXAMPLE 1:
input: Ich möchte in eine Stadt mit guten Kunstmuseen gehen.

output:

Reason 1: I should list cities with art museums as preferences, since no region
was mentioned I should look for region "World"

Say 1: Ich könnte Ihnen viele Reiseziele nennen, die weltberühmte Kunstmuseen aufweisen.

Act 1: list_cities(preferences: ["art museums|Kunstmuseen"], region: ["World|Welt"]))

Observe 2: Ich möchte in Europa bleiben.

Reason 2: A region has been mentioned, I should set the "region" parameter with Europe.

Say 2: Klingt gut, ich zeige Ihnen nur die Liste der Städte in Europa.

Act 2: list_cities(preferences: ["art museums|Kunstmuseen"], region: ["Europe|Europa"])

Observe 3: OK, ich glaube, ich möchte nach Berlin fliegen und ich wäre auch daran interessiert, dort ein paar gute Restaurants zu besuchen.

Reason 3: The customer chose a city, Berlin, so I should choose the show_itineary function.
I should also add "restaurants" to the existing preferences.

Say 3: Great, here is some more information about Berlin including a few
restaurants you may like.

Act 3: show_itinerary(preferences: ["restaurants|Restaurants", "art museums|Kunstmuseen"], city: "Berlin")



EXAMPLE 2:
input: Ich bin in Genf und möchte nächsten Sommer in Spanien einen Strandurlaub machen.

output:

Reason 1: The customer is coming from Geneva, their preferences are
"beach vacation" and they are interested in Spain as a region. I don't know
when "next year" is so I should just ignore it.

Say 1: Klingt gut. Ich habe viele passende Reiseziele für einen Strandurlaub in
Spanien.

Act 1: list_cities(origin: "Geneva", preferences: ["beach vacation|Strandurlaub"], region: ["Spain|Spanien"])

Observe 2: Ich möchte auch gerne in Clubs gehen.

Reason 2: I should add "nightclubs" to the previous preferences.

Say 2: In Ordnung, ich kann nach Reisezielen suchen, die für ihr pulsierendes Nachtleben bekannt sind.

Act 2: list_cities(origin: "Geneva", preferences: ["beach vacation|Strandurlaub", "nightclubs|Nachtclubs"], region: ["Spain|Spanien"])

Observe 3: Aber ich möchte auch Zugang zu Museen haben.

Reason 3: I should expand the list of preferences to include museums.

Say 3: OK, ich werde auch nach Städten mit Museen suchen.

Act 3: list_cities(origin: "Geneva", preferences: ["beach vacation|Strandurlaub", "nightclubs|Nachtclubs", "museums|Museen"], region: ["Spain|Spanien"])

Observe 4: OK, wie wäre es mit Städten ausserhalb Spaniens?

Reason 4: I should remove the previous region preference for Spain.

Say 4: Sicher, hier ist die Liste der Städte ausserhalb Spaniens, die für einen Strandurlaub geeignet sind und Museen und Nachtclubs haben.

Act 4: list_cities(origin: "Geneva", preferences: ["beach vacation|Strandurlaub", "nightclubs|Nachtclubs", "museums|Museen"])


EXAMPLE 3:
input: Ich möchte einen günstigen Wochenendtrip machen.

output:

input: Direktflüge in die USA ab Genf

Reason 1: I should update origin to "Geneva" and update the region to "USA". The
customer wants direct flights so I should add 'direct flight' as a preference
and also set the 'direct' parameter to "yes".

Say 1: Hier sind einige Städte mit Direktflügen ab Genf:

Act 1: list_cities(preferences: ["direct flight|Direktflug"], origin: "Geneva", region:["USA|USA"], direct: "yes")

Observe 2: Ich möchte auf die Balearen reisen

Reason 2: The Balearic Islands is a region, so I should look for cities in that region.

Act 2: list_cities(preferences: ["direct flight|Direktflug"], origin: "Geneva", region:["Balearic Islands|Balearen"], direct: "yes")

Say 2: Hier sind einige Ziele auf den Balearen mit Direktflügen ab Genf:

Observe 3: Was ist mit Orten, die mehr als 8 Flugstunden von hier entfernt sind?

Reason 3: I should look at destinations around the world reachable by a long haul flight.

Act 3: list_cities(preferences: ["direct flight|Direktflug", "long haul|Langstrecke"], origin: "Geneva", region:["World|Welt"], direct: "yes")

Say 3: Hier sind einige Fernreiseziele auf der ganzen Welt:

Observe 4: Entfernen Sie die Präferenz für Direktflüge

Reason 4: I will remove the preference "direct flight|Direktflug" and also the direct parameter.

Act 4: list_cities(preferences: ["long haul|Langstrecke"], origin: "Geneva", region:["World|Welt"])

Observe 5: Zeigen Sie mir Orte, an denen im Jahr 2025 große Sportveranstaltungen stattfinden

Reason 5: I should add "sports events" to the preferences. I don't know how to handle years
so I should just ignore it.

Act 5: list_cities(preferences: ["long haul|Langstrecke", "sports events"], origin: "Geneva", region:["World|Welt"])

Say 5: Hier sind einige Reiseziele, an denen Sportveranstaltungen auf der ganzen Welt stattfinden:



EXAMPLE 4:
input: Ich möchte grosse Städte erkunden, ich fliege von Zürich

Reason 1: The customer has preferences "big cities" with origin Zurich, I should
look for locations in region "World|Welt" as no region was specified.

Say 1: Sicher, hier sind einige grossartige Grossstädte, die Sie erkunden können:

Act 1: list_cities(preferences: ["big cities[Grossstädte]"], origin: "Zurich", region: ["World|Welt"])

Observe 2: Ich bleibe lieber in der Nähe

Reason 2: The customer implies they want to stay close. Since
they are flying from Zurich, I will narrow down the region to Europe

Say 2: Sicher, hier sind einige Orte, die in der Nähe von Zürich liegen.

Act 2: list_cities(preferences: ["big cities[Grossstädte]"], origin: "Zurich", region: ["Europe|Europa"])


EXAMPLE 5:
input:

wir sind eine vierköpfige Familie und wir möchten einen Strandurlaub machen

output:

Reason 1: I should add "family friendly" and "beach vacation" as preferences.
Since no region was mentioned, I should look  for the region "World"

Say 1: Ich habe viele familienfreundliche Reiseziele, die perfekt für einen
Strandurlaub wären.

Act 1: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich"], region: ["World|Welt"])

Observe 2: wir sind nicht sehr reich

Reason 2: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 2: Ich kann nach einigen erschwinglichen Optionen für Ihren Familienstrandurlaub suchen.

Act 2: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich"], max_price: 500, region: ["World|Welt"])

Observe 3: Wir möchten in die USA reisen und ein paar gute Museen sehen

Reason 3: The customer chose the US, so I should show them more detailed
information about the US.

Say 3: Grossartig, hier sind einige weitere Informationen über die USA, einschliesslich einiger
Museen, die Ihnen gefallen könnten.

Act 3: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "museums|Museen"], region: ["US|USA"])

Observe 4: wir können auch Europa in Betracht ziehen

Reason 4: The customer is open to considering Europe, so I should expand the
region to include Europe.

Say 4: Europa ist auch eine gute Wahl für einen Familienstrandurlaub. Lassen Sie mich ein paar mögliche Orte nachschlagen.

Act 4: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "museums|Museen"], region: ["US|USA", Europe|Europa"])

Observe 5: wir wollen keine Museen sehen, sondern lieber gute Restaurants

Reason 5: The customer does not want to see museums, so I should remove
museums from the list of preferences.

Say 5: In Ordnung, ich werde nach Städten mit guten Restaurants suchen.

Act 5: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "restaurants|Restaurants"], region: ["US|USA", "Europe|Europa"])

Observe 6: wir wollen nicht, dass die Reise zu teuer wird

Reason 6: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 6: Ich kann nach einigen erschwinglichen Optionen für Ihren Familienstrandurlaub suchen.

Act 6: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "restaurants|Restaurants"], region: ["US|USA", "Europe|Europa"], max_price: 500)

Observe 7: Und wir wollen für 1 1/2 Wochen reisen

Reason 7: The customer specified the duration of the trip to be 1 and a half weeks, so I should update the duration parameter
to the closest round number of days.

Say 7: Sicher, ich werde nach 1 1/2 Wochen langen Reisen suchen.

Act 7: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "restaurants|Restaurants"], region: ["US|USA", "Europe|Europa"], max_price: 500, duration: 11)

Observe 8: Wir wollen nicht nach Europa fahren

Reason 8: The customer does not wish to go to Europe, so I should remove that from the list of regions.

Say 8: Verstanden. Entferne die Städte in Europa von der Liste.

Act 8: list_cities(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "restaurants|Restaurants"], region: ["US|USA"], max_price: 500, duration: 14)

Observe 9: wir mögen Los Angeles.

Reason 9: The customer chose Los Angeles, so I should show them more detailed
information about Los Angeles.

Say 9: Grossartig, hier sind einige weitere Informationen über Los Angeles, einschliesslich einiger
Restaurants, die Ihnen gefallen könnten.

Act 9: show_itinerary(preferences: ["beach vacation|Strandurlaub", "family friendly|familienfreundlich", "restaurants|Restaurants"], city: "Los Angeles", duration: 14)


EXAMPLE 6:
input: Ich würde nächste Woche gerne Live-Jazz in London sehen

output:

Reason 1: The customer mentioned a city, so I should show them an
itinerary for that city, with "jazz" as preferences. I don't know when
"next week" is so I can ignore it.

Say 1: Grossartige Wahl, London ist ein ausgezeichneter Ort, um Live-Jazz zu geniessen.

Act 1: show_itinerary(preferences: ["jazz|Jazz"], city: "London")



EXAMPLE 7:
input:  Ich möchte im Juli eine Wanderung machen.

output:

Reason 1: The customer has hiking as a preference hiking and they want to do so
in July, which is the 7th month. Since no region was specified I will look all over the world.


Say 1: Grossartig, hier sind ein paar Optionen für Ihre Wanderreise.

Act 1: list_cities(preferences: ["hiking|Wandern"], start_month: 7, end_month: 7, region: ["World|Welt"])

Observe 2: Ich würde gerne irgendwo auf die Mittelmeerinseln gehen

Reason 2: I should update the region to be "Mediterranean Islands".

Say 1: Ich werde nach Orten auf den Mittelmeerinseln suchen:

Act 1: list_cities(preferences: ["hiking"], start_month: 7, end_month: 7, region: ["Mediterranean Islands|Mittelmeerinseln"])


EXAMPLE 8:
Input: Zeigen Sie mir warme Reiseziele in Europa, aber nicht in Italien.

Output:

Reason 1: The customer's would like to visit a warm place, and I should find locations that are in Europe, but outside of Italy.

Say 1: Hier sind einige Optionen für warme Orte in Europa und außerhalb Italiens.

Act 1: list_cities(preferences: ["warm|"warm"], region: ["Europe|Europa", "Not in Italy|Nicht in Italien"])

EXAMPLE 9:
input: Ich möchte Skifahren

output:

Reason 1: I should add 'skiing' as preferences. Since no region was mentioned I should look
for region "World|Welt".

Say 1: Hier sind einige beliebte Skigebiete auf der ganzen Welt:

Act 1: list_cities(preferences: ["skiing"], region: ["World|Welt"])



--- EXAMPLES END ---

"""
