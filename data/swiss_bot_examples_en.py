EXAMPLES = """
--- EXAMPLES BEGIN ---

EXAMPLE 1:
input: I would like to go to a city with good art museums.

output:

Reason 1: I should list cities with art museums as preferences, since no region
was mentioned I should look for region "World"

Say 1: I could search you many destinations that boast world famous art museums.

Act 1: list_cities(preferences: ["art museums"], region: ["World"])

Observe 2: I would like to stay in Europe.

Reason 2: A region has been mentioned, I should set the "region" parameter with Europe.

Say 2: Sounds good, showing you the list of cities in Europe only.

Act 2: list_cities(preferences: ["art museums"], region: ["Europe"])

Observe 3: OK, I think I would like to go to Berlin and I would also be
interested in going to some good restaurants there.

Reason 3: The customer chose a city, Berlin, so I should choose the show_itineary function.
I should also add "restaurants" to the existing preferences.

Say 3: Great, here is some more information about Berlin including a few
restaurants you may like.

Act 3: show_itinerary(preferences: ["restaurants", "art museums"], city: "Berlin")


EXAMPLE 2:
input: I am in Geneva and I would like to go on a beach vacation in Spain next year.

output:

Reason 1: The customer is coming from Geneva, their preferences are
"beach vacation" and they are interested in Spain as a region. I don't know
when "next year" is so I should just ignore it.

Say 1: Sounds good. I have lots of suitable destinations for a beach vacation in
Spain.

Act 1: list_cities(origin: "Geneva", preferences: ["beach vacation"], region: ["Spain]")

Observe 2: I would also like to go clubbing.

Reason 2: I should add "nightclubs" to the previous preferences.

Say 2: Alright, I can look for destinations known for their vibrant night life.

Act 2: list_cities(origin: "Geneva", preferences: ["beach vacation", "nightclubs"], region: ["Spain"])

Observe 3: But I would like to also have access to museums.

Reason 3: I should expand the list of preferences to include museums.

Say 3: OK, I will also look for cities with museums.

Act 3: list_cities(origin: "Geneva", preferences: ["beach vacation", "nightclubs", "museums"], region: ["Spain"])

Observe 4: OK, how about cities outside Spain?

Reason 4: I should remove the previous region preference for Spain.

Say 4: Sure, here are the list of cities outside Spain suitable for a beach
vacation and have museums and nightclubs.

Act 4: list_cities(origin: "Geneva", preferences: ["beach vacation", "nightclubs", "museums"])


EXAMPLE 3:
input: direct flights to the US from Geneva

Reason 1: I should update origin to "Geneva" and update the region to "USA". The
customer wants direct flights so I should add 'direct flight' as a preference
and also set the 'direct' parameter to "yes".

Say 1: Here are some cities with direct flights from Geneva:

Act 1: list_cities(preferences: ["direct flight"], origin: "Geneva", region:["US"], direct: "yes")

Observe 2: I want to go the Balearic Islands

Reason 2: The Balearic Islands is a region, so I should look for cities in that region.

Act 2: list_cities(preferences: ["direct flight"], origin: "Geneva", region:["Balearic Islands"], direct: "yes")

Say 2: Here are some destinations in the Balearic Islands with direct flights from Geneva:

Observe 3: What about places with more than a 8 hour flight from here?

Reason 3: I should look at destinations around the world reachable by a long haul flight.

Act 3: list_cities(preferences: ["direct flight", "long haul"], origin: "Geneva", region:["World"], direct: "yes")

Say 3: Here are some long haul destinations around the world:

Observe 4: Remove the preference for direct flight

Reason 4: I will remove the preference "direct flight" and also the direct parameter.

Act 4: list_cities(preferences: ["long haul"], origin: "Geneva", region:["World"])

Observe 5: Show me places that have big sports events in 2025

Reason 5: I should add "sports events" to the preferences. I don't know how to handle years
so I should just ignore it.

Act 5: list_cities(preferences: ["long haul", "sports events"], origin: "Geneva", region:["World"])

Say 5: Sure, here are some destinations that host sports events around the world:


EXAMPLE 4:
input: I'd like to explore big cities, I'm flying from Zurich

Reason 1: The customer has preferences "big cities" with origin Zurich, I should
look for locations in region "World" as no region was specified.

Say 1: Sure, here are some great big cities you can explore:

Act 1: list_cities(preferences: ["big cities"], origin: "Zurich", region:["World"])

Observe 2: I'd rather stay close

Reason 2: The customer implies they want to stay close. Since
they are flying from Zurich, I will narrow down the region to Europe

Say 2: Sure, here are some locations that are close to Zurich.

Act 2: list_cities(preferences: ["big cities"], origin: "Zurich", region: ["Europe"])


EXAMPLE 5:
input:

we are a family of four and we would like to go on a beach vacation

output:

Reason 1: I should add "family friendly" and "beach vacation" as preferences.
Since no region was mentioned, I should look  anywhere in the World.

Say 1: I have many family friendly destinations that would be perfect for a
beach vacation.

Act 1: list_cities(preferences: ["beach vacation", "family friendly"], region: ["World"])

Observe 2: we are not very rich

Reason 2: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 2: I can search for some affordable options for your family beach
vacation.

Act 2: list_cities(preferences: ["beach vacation", "family friendly"], max_price: 500, region: ["World"])

Observe 3: We would like to go to the US and see some good museums

Reason 3: The customer chose the US, so I should show them more detailed
information about the US.

Say 3: Great, here is some more information about the US including a few
museums you may like.

Act 3: list_cities(preferences: ["beach vacation", "family friendly", "museums"], region: ["US"])

Observe 4: we can also consider Europe

Reason 4: The customer is open to considering Europe, so I should expand the
region to include Europe.

Say 4: Europe is also a great choice for a family beach vacation. Let me look
up a few possible locations.

Act 4: list_cities(preferences: ["beach vacation", "family friendly", "museums"], region: ["US", "Europe"])

Observe 5: we don't want to see museums, but we would rather prefer good restaurants

Reason 5: The customer does not want to see museums, so I should remove
museums from the list of preferences.

Say 5: Alright, I will look for cities with good restaurants.

Act 5: list_cities(preferences: ["beach vacation", "family friendly", "restaurants"], region: ["US", "Europe"])

Observe 6: we don't want the trip to be too expensive

Reason 6: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 6: I can search for some affordable options for your family beach
vacation.

Act 6: list_cities(preferences: ["beach vacation", "family friendly", "restaurants"], region: ["US", "Europe"], max_price: 500)

Observe 7: And we want to go for 1 and a half weeks

Reason 7: The customer specified the duration of the trip to be 1 and a half weeks, so I should update the duration parameter
to the closest round number of days.

Say 7: Sure, I will look for 1 and a half week long trips.

Act 7: list_cities(preferences: ["beach vacation", "family friendly", "restaurants"], region: ["US", "Europe"], max_price: 500, duration: 11)

Observe 8: We don't want to go to europe

Reason 8: The customer does not wish to go to Europe, so I should remove that from the list of regions.

Say 8: Understood. Removing the cities in Europe from the list.

Act 8: list_cities(preferences: ["beach vacation", "family friendly", "restaurants"], region: ["US"], max_price: 500, duration: 11)

Observe 9: we like Los Angeles.

Reason 9: The customer chose Los Angeles, so I should show them more detailed
information about Los Angeles.

Say 9: Great, here is some more information about Los Angeles including a few
restaurants you may like.

Act 9: show_itinerary(preferences: ["beach vacation", "family friendly", "restaurants"], city: "Los Angeles", duration: 14)


EXAMPLE 6:
input: I would like to see live jazz in London next week

output:

Reason 1: The customer mentioned a city, so I should show them an
itinerary for that city, with "jazz" as preferences. I don't know when
"next week" is so I can ignore it.

Say 1: Great choice, London is a excellent place for enjoying live jazz.

Act 1: show_itinerary(preferences: ["jazz"], city: "London")



EXAMPLE 7:
input: I would like to go on a hiking trip in July.

output:

Reason 1: The customer has hiking as a preference hiking and they want to do so
in July, which is the 7th month. Since no region was specified I will look in
the region "World"

Say 1: Here are a few options for your hiking trip.

Act 1: list_cities(preferences: ["hiking"], start_month: 7, end_month: 7, region: ["World"])

Observe 2: I would like to go somewhere in the Mediterranean Islands

Reason 2: I should update the region to be "Mediterranean Islands".

Say 1: I will look for places in the Mediterranean Islands:

Act 1: list_cities(preferences: ["hiking"], start_month: 7, end_month: 7, region: ["Mediterranean Islands"])



EXAMPLE 8:
input: Show me warm destinations in Europe, but not in Italy.

output:

Reason 1: The customer's would like to visit a warm place, and I should find locations that are in Europe, but outside of Italy.

Say 1: Here are a few options of warm places in Europe and outside of Italy.

Act 1: list_cities(preferences: ["warm"], region: ["Europe", "Not in Italy"])


EXAMPLE 9:
input: I want to ski

output:

Reason 1: I should add 'skiing' as preferences. Since no region was mentioned I should look
for region "World".

Say 1: Here are some popular ski destinations around the world:

Act 1: list_cities(preferences: ["skiing"], region: ["World"])


--- EXAMPLES END ---

"""
