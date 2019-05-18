
Veekun's Pokedex data extractor

This is a small script that works on Veekun's Pokedex : https://github.com/veekun/pokedex Its goal is to extract only relevant information for another small project, a fight simulator in French. The extracted information is copied to a sqlite database. This is not intended to be used by anyone else but who knows.

How to run :
-Download veekun_extractor.py
-Download Veekun's pokedex at https://github.com/veekun/pokedex
-Locate the file pokedex.sqlite. It should be at pokedex/pokedex/data/pokedex.sqlite
-Copy its path into the variable "veekun_database_location" at the top of veekun_extractor.py
-Put your desired output filename in the variable "sunrise_database_location" at the top of veekun_extractor.py
-Set variable "skip_long_stuff" to False, still in veekun_extractor.py
-Run veekun_extractor.py

Generated tables description:

table pokemons
	id : id numérique de ce pokémon. pour les pokémons ayant plusieurs formes (forme pouvant changer pendant le combat comme morphéo ou les méga-évolutions, les formes d'alola, rotom...) une forme = un pokémon distinct = un id distinct
	nom : nom du pokémon, affichable pour l'utilisateur. du type "Pikachu", "Raichu d'Alola", "Méga Dracaufeu", "Motisma tondeuse"... a toujours une majuscule
	type1 : type du poké (normal, feu, eau...)
	type2 : pour les double-types, type secondaire du poké
	pv : valeur de la stat PV. int.
	attaque : idem
	defense : idem
	attaque_speciale : idem
	defense_speciale : idem
	vitesse : idem
	taux_capture : catch rate du pokémon. certains pokémons ont une valeur vide (méga-évo...)
	poids : poids du pokémon en hectogrammes. 1,5kg par exemple est représenté 150
	forme : pour les pokémons étant une forme, donne le type de forme. "alola", "mega", ou des trucs spéciaux. les pokémons normaux ont le champ vide
	base_forme : pour les pokémons étant une forme, l'ID du pokémon base. ex pour "pikachu d'alola" renvoie vers "pikachu"

table attaques
	cette table est susceptible d'avoir de nouvelles colonnes dans l'avenir pour traiter des effets particuliers
	id : id numérique de cette attaque
	nom : nom affichable pour l'utilisateur (Charge, Rugissement...)
	type : type de l'attaque (normal, feu...)
	puissance : puissance de l'attaque (60, 120...) peut être vide pour les attaques non-offensives
	precision : précision de l'attaque, 100 max, peut être vide pour les attaques réussissant à coup sûr
	priorite : priorité de l'attaque
	classe : physique, speciale ou no_damage
	effet_texte : contient la description de l'attaque affichable pour l'utilisateur qui décrit tous les effets particuliers
	chance_effet_texte : pourcentage de chance que l'effet spécial de cette attaque se réalise, comme décrit colonne "effet_texte". Les effets codés comme la peur ont leur pourcentage de chance de se réaliser ici. attention à ne pas confondre avec la colonne chance_d_infliger_statut
	statut_inflige : pour les attaques qui infligent un statut, précise de quel statut il s'agit (sommeil, brûlure, paralysie...)
	chance_d_infliger_statut : pourcentage de chance d'infliger le statut précisé dans la colonne statut_inflige
	pourcentage_pv_soignes : pour les attaques comme synthèse qui ne font que restaurer des PV, indique le pourcentage des PVs totaux du lanceur qui sont restaurés. à ne pas confondre avec pourcentage_pv_draines pour des attaques qui infligent des dégâts comme giga-sangsue
	pourcentage_pv_draines : pour les attaques comme giga-sangsue, l'attaque enlève des PV à l'adversaire, N% des PVs retirés à la cible sont restaurés au lanceur. Par exemple giga-sangsue draine 50% des PVs retirés à la cible, sa valeur dans cette colonne est donc 50
	chance_apeurer : pour les attaques comme étonnement ou morsure, donne le pourcentage de chances que la cible soit apeurée
	taux_critique : chances que cette attaque fasse un coup critique. "normal" : 4.17%, "eleve":12.5%,"tres eleve":50%, "toujours critique":100%

	cible : quel(s) pokémon(s) est/sont ciblé(s) par cette attaque.
		cibles normales :
		"au choix sauf lanceur" : attaque offensive classique comme charge
		"tous les adversaires" : attaque offensive comme tranch'herbe ou attaque de terrain comme pic toxik
		"lanceur" : attaque de boost comme boul'armure
		"tous les alliés" : généralement une attaque ciblant le terrain comme mur lumière
		"tous sauf lanceur" : attaque comme séisme ou surf qui touche aussi bien les alliés que les ennemis
		"tous" : généralement attaque de terrain comme distortion

		cibles rencontrées uniquement sur des attaques spécifiques :
		"random" : on ne choisit pas la cible (cas de mania, lutte, danse-fleur, colère et brouhaha)
		"truc spécifique" : cible le pokémon ayant attaqué le lanceur (cas de riposte voile miroir et fulmifer) ou la cible varie selon des conditions spécifiques (cas de malédiction)
		"utilisateur et alliés" : soigne tout le monde (cas de glas de soin et aromathérapie) ou booste ceux ayant pour talent plus ou minus (cas de magné-contrôle et engrenage) (donc sert à rien pour ces 2 derniers)
		"allié" : attaque boostant un allié (cas de coup d'main et brume capiteuse) et cas de mains jointes qui est une trempette qui ne marche qu'en double/triple et n'existe que pour des poké spéciaux d'event.
		"lanceur ou allié" : attaque de boost (cas d'acupression)
		"au choix" : peut cibler n'importe quel allié ou adversaire (cas de moi d'abord)
	
	puissance_pv_fixes : pour les attaques qui enlèvent un nombre de PV fixes à la cible (draco-rage et sonicboom) indique combien de PV. une attaque ayant une valeur ici aura une valeur vide dans la colonne "puissance"
	puissance_pourcentage : pour les attaques qui enlèvent N% des PV restants à la cible (comme croc fatal) indique combien de %. une attaque ayant une valeur ici aura une valeur vide dans la colonne "puissance"
	categorie_chiante : tag certaines attaques ayant une manière particulière de fonctionner
		ohko : attaque mettant la cible KO
		niveau : inflige N PV de dégâts où N est égal au niveau du lanceur
		attaque z : est une attaque z. surprise.
		poids : la puissance dépend de la différence de poids entre la cible et le lanceur
		vitesse : la puissance dépend de la différence de vitesse entre la cible et le lanceur
		pp : la puissance dépend des PP restants, non-applicable sur sunrise
		objet tenu : l'effet dépend de l'objet tenu par le lanceur, non-applicable sur sunrise

	informations : vide par défaut, servira à ajouter des infos à la main. contient actuellement des [code] pour des trucs repérés dans texte_effet
	
table attaques_stats_adversaire
et
table attaques_stats_lanceur
	pour les attaques modifiant les stats comme rugissement ou puissance, indique qui est la cible du changement (lanceur ou adversaire), quelle est la stat ciblée (attaque, défense...) et de combien de niveaux est le changement (-3, -2, -1, +1, +2, +3). Une attaque peut baisser les stats du lanceur (surpuissance) ou augmenter celles de l'adversaire
	les mêmes colonnes sont présentes dans les deux tables

	id_attaque : correspond à "id" dans la table "attaques"
	nom_attaque : correspond à "nom" dans la table "attaques". j'ai mis id et nom pour faciliter les recherches
	attaque : -3/-2/-1/0/+1/+2/+3
	defense : idem
	attaque_speciale : idem
	defense_speciale : idem
	vitesse : idem
	precision : idem, attaques comme jet de sable
	esquive : idem, attaques comme lilliput

table apprentissage
	définit quel pokémon apprend quelle attaque par quel moyen
	chaque entrée représente une correspondance pokémon/attaque. Chaque pokémon aura une entrée pour chaque attaque qu'il peut apprendre. Chaque pokémon et chaque attaques apparaitront donc chacun dans de nombreuses entrées différentes
	pour les pokémons pouvant apprendre une même attaque par plusieurs méthodes différentes, seule une seule entrée a été conservée pour éviter les doublons. dans ces cas-là, j'ai gardé de préférence la méthode "niveau", et sinon la méthode "ct"
	pokemon_id : correspond à "id" dans la table "pokemons"
	attaque_id : correspond à "id" dans la table "attaques"
	methode : comment le pokémon apprend cette attaque. niveau/reproduction/maitre_capacites/ct/forme. forme correspond à des cas particuliers, notamment les formes de rotom, mais à terme cette méthode devrait disparaitre
	niveau : pour les attaques apprises par niveau, à quel niveau cette attaque est apprise. pour les pokémons pouvant apprendre une même attaque à plusieurs niveaux différents (une première fois par la pré-évo puis à un niveau plus élevé pour l'évo) le niveau le moins élevé a été gardé



