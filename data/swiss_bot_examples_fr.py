EXAMPLES = """
--- EXAMPLES BEGIN ---

EXAMPLE 1:

input: j’aimerais aller dans une ville avec de bons musées d’art.

output:

Reason 1: I should list cities with art museums as preferences, since no region
was mentioned I should look for region "World"

Say 1: Je peux vous chercher de nombreuses destinations qui abritent des musées d’art de renommée mondiale.

Act 1: list_cities(preferences: ["art museums[musées d'art]"], region: ["World|Monde"])

Observe 2: J’aimerais rester en Europe.

Reason 2: A region has been mentioned, I should set the "region" parameter with Europe.

Say 2: Ça a l’air bien, je vous montre la liste des villes d’Europe uniquement.

Act 2: list_cities(preferences: ["art museums[musées d'art]"], region: ["Europe|Europe"])

Observe 3: ok, je crois que j’aimerais aller à Berlin et je serais également intéressé à aller dans de bons restaurants là-bas.

Reason 3: The customer chose a city, Berlin, so I should choose the show_itineary function.
I should also add "restaurants" to the existing preferences.

Say 3: Super, voici quelques informations supplémentaires sur Berlin, y compris quelques restaurants qui pourraient vous plaire.

Act 3: show_itinerary(preferences: ["restaurants|restaurants", "art museums[musées d'art]]", city: "Berlin")


EXAMPLE 2:

input: je suis à Genève et j’aimerais partir en vacances à la plage en Espagne l’année prochaine.

output:

Reason 1: The customer is coming from Geneva, their preferences are
"beach vacation" and they are interested in Spain as a region. I don't know
when "next year" is so I should just ignore it.

Say 1: Ça a l’air bien. J’ai beaucoup de destinations appropriées pour des vacances à la plage en Espagne.

Act 1: list_cities(origin: "Geneva", preferences: ["beach vacation|vacances à la plage"], region: ["Spain|Espagne"])

Observe 2 : j’aimerais aussi aller en boîte de nuit.

Reason 2: I should add "nightclubs" to the previous preferences.

Say 2: Très bien, je peux chercher des destinations connues pour leur vie nocturne animée.

Act 2: list_cities(origin: "Geneva", preferences: ["beach vacation|vacances à la plage", "nightclubs[boîtes de nuit]"], region: ["Spain|Espagne"])

Observe 3 : mais j’aimerais aussi avoir accès à des musées.

Reason 3: I should expand the list of preferences to include museums.

Say 3: Ok, je vais aussi chercher des villes avec des musées.

Act 3: list_cities(origin: "Geneva", preferences: ["beach vacation|vacances à la plage", "nightclubs[boîtes de nuit]", "museums|musées"], region: ["Spain|Espagne"])

Observe 4: ok, qu’en est-il des villes en dehors de l’Espagne ?

Reason 4: I should remove the previous region preference for Spain.

Say 4: Bien sûr, voici la liste des villes en dehors de l’Espagne qui conviennent pour des vacances à la plage et qui ont des musées et des boîtes de nuit.

Act 4: list_cities(origin: "Geneva", preferences: ["beach vacation|vacances à la plage", "nightclubs[boîtes de nuit]", "museums|musées"])

EXAMPLE 3:
input: vols directs vers les États-Unis depuis Genève

Reason 1: I should update origin to "Geneva" and update the region to "USA". The
customer wants direct flights so I should add 'direct flight' as a preference
and also set the 'direct' parameter to "yes".

Say 1:  Voici quelques villes avec des vols directs au départ de Genève :

Act 1: list_cities(preferences: ["direct flight|vol direct"], origin: "Geneva", region:["US|États-Unis"], direct: "yes")

Observe 2: Je veux aller aux îles Baléares

Reason 2: The Balearic Islands is a region, so I should look for cities in that region.

Act 2: list_cities(preferences: ["direct flight|vol direct"], origin: "Geneva", region:["Balearic Islands|îles Baléares"], direct: "yes")

Say 2: Voici quelques destinations dans les îles Baléares avec des vols directs au départ de Genève :

Observe 3: Et les endroits avec plus de 8 heures de vol d'ici ?

Reason 3: I should look at destinations around the world reachable by a long haul flight.

Act 3: list_cities(preferences: ["direct flight|vol direct", "long haul|long-courrier"], origin: "Geneva", region:["World|Monde"], direct: "yes")

Say 3:  Voici quelques destinations long-courriers dans le monde :

Observe 4: Supprimez la préférence pour les vols directs

Reason 4: I will remove the preference "direct flight" and also the direct parameter.

Act 4: list_cities(preferences: ["long haul|long-courrier"], origin: "Geneva", region:["World|Monde"])

Observe 5: Montrez-moi les endroits qui accueillent de grands événements sportifs en 2025

Reason 5: I should add "sports events" to the preferences. I don't know how to handle years
so I should just ignore it.

Act 5: list_cities(preferences: ["long haul|long-courrier", "sports events|évènements sportifs"], origin: "Geneva", region:["World|Monde"])

Say 5:  Bien sûr, voici quelques destinations qui accueillent des événements sportifs dans le monde :


EXAMPLE 4:
input: j’aimerais explorer les grandes villes, je pars de Zurich

Reason 1: The customer has preferences "big cities" with origin Zurich, I should
look for locations in region "World" as no region was specified.

Say 1: Bien sûr, voici quelques grandes villes formidables que vous pouvez explorer :

Act 1: list_cities(preferences: ["big cities|grandes villes"], origin: "Zurich", region: ["World|Monde"])

Observe 2: je préfère rester à proximité

Say 2: Bien sûr, voici quelques endroits proches de Zurich.

Act 2: list_cities(preferences: ["big cities|grandes villes"], origin: "Zurich", region: ["Europe|Europe"])

EXAMPLE 5:
input: nous sommes une famille de quatre personnes et nous aimerions partir en vacances à la plage

output:

Reason 1: I should add "family friendly" and "beach vacation" as preferences.
Since no region was mentioned, I should look  anywhere in the World, so I will add "World" as region.

Say 1: J’ai de nombreuses destinations familiales qui seraient parfaites pour des vacances à la plage.

Act 1: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales"], , region: ["World|Monde"])

Observe 2: nous ne sommes pas très riches

Reason 2: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 2: Je peux chercher des options abordables pour vos vacances à la plage en famille.

Act 2: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales"], max_price: 500)

Observe 3: nous aimerions aller aux États-Unis et visiter de bons musées

Reason 3: The customer chose the US, so I should show them more detailed
information about the US.

Say 3: Super, voici quelques informations supplémentaires sur les États-Unis, y compris quelques musées qui pourraient vous plaire.

Act 3: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "museums|musées"], region: ["US|États-Unis"])

Observe 4: nous pouvons également envisager l’Europe

Reason 4: The customer is open to considering Europe, so I should expand the
region to include Europe.

Say 4: L’Europe est également un excellent choix pour des vacances à la plage en famille. Laissez-moi chercher quelques endroits possibles.

Act 4: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "museums|musées"], region: ["US|États-Unis", "Europe|Europe"])

Observe 5: nous ne voulons pas visiter de musées, mais nous préférerions de bons restaurants

Reason 5: The customer does not want to see museums, so I should remove
museums from the list of preferences.

Say 5: Très bien, je vais chercher des villes avec de bons restaurants.

Act 5: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "restaurants|restaurants"], region: ["US|États-Unis", "Europe|Europe"])

Observe 6: nous ne voulons pas que le voyage soit trop cher

Reason 6: The customer is looking for a budget vacation, so I should cap
the price at a reasonable maximum, say 500.

Say 6: Je peux chercher des options abordables pour vos vacances à la plage en famille.

Act 6: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "restaurants|restaurants"], region: ["US|États-Unis", "Europe|Europe"], max_price: 500)

Observe 7: et nous voulons partir pour une semaine et demie

Reason 7: The customer specified the duration of the trip to be 1 and a half weeks, so I should update the duration parameter
to the closest round number of days.

Say 7: Bien sûr, je vais chercher des voyages d’une semaine et demie.

Act 7: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "restaurants|restaurants"], region: ["US|États-Unis", "Europe|Europe"], max_price: 500, duration: 11)

Observe 8: nous ne voulons pas aller en Europe

Reason 8: The customer does not wish to go to Europe, so I should remove that from the list of regions.

Say 8: Compris. Suppression des villes d’Europe de la liste.

Act 8: list_cities(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "restaurants|restaurants"], region: ["US|États-Unis"], max_price: 500, duration: 11)

Observe 9: nous aimons Los Angeles.

Reason 9: The customer chose Los Angeles, so I should show them more detailed
information about Los Angeles.

Say 9: Super, voici quelques informations supplémentaires sur Los Angeles, y compris quelques restaurants qui pourraient vous plaire.

Act 9: show_itinerary(preferences: ["beach vacation|vacances à la plage", "family friendly|familiales", "restaurants|restaurants"], city: "Los Angeles", max_price: 500, duration: 11)


EXAMPLE 6:
input: j’aimerais voir du jazz en direct à Londres la semaine prochaine

output:

Reason 1: The customer mentioned a city, so I should show them an
itinerary for that city, with "jazz" as preferences. I don't know when
"next week" is so I can ignore it.

Say 1: Excellent choix, Londres est un endroit idéal pour apprécier du jazz en direct.

Act 1: show_itinerary(preferences: ["jazz|Jazz"], city: "London")


EXAMPLE 7:
input: j’aimerais faire une randonnée en juillet.

output:

Reason 1: The customer has hiking as a preference hiking and they want to do so
in July, which is the 7th month. Since no region was specified I will look in
the region "World"


Say 1: Voici quelques options pour votre randonnée.

Act 1: list_cities(preferences: ["hiking|randonnée"], start_month: 7, end_month: 7, region: ["World|Monde"])

Observe 2: J'aimerais aller quelque part dans les îles méditerranéennes

Reason 2: I should update the region to be "Mediterranean Islands".

Say 1: Je vais chercher des endroits dans les îles méditerranéennes :

Act 1: list_cities(preferences: ["hiking|randonnée"], start_month: 7, end_month: 7, region: ["Mediterranean Islands|îles méditerranéennes"])


EXAMPLE 8:
input: Montre-moi des destinations chaleureuses en Europe, mais pas en Italie.

output:

Reason 1: The customer's would like to visit a warm place, and I should find locations that are in Europe, but outside of Italy.

Say 1: Voici quelques options d’endroits chauds en Europe et en dehors de l’Italie.

Act 1: list_cities(preferences: ["warm|chaud"], region: ["Europe|L'Europe", "Not in Italy|pas en Italie"])

EXAMPLE 9:
input: je veux skier

output:

Reason 1: I should add 'skiing' as preferences. Since no region was mentioned I should look
for region "World".

Say 1: Voici quelques destinations de ski populaires à travers le monde :

Act 1: list_cities(preferences: ["skiing|ski"], region: ["World|Monde"])


--- EXAMPLES END ---
"""
