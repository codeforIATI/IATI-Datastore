export default {
  codeForIATIProject: 'Un projet de Code pour IITA',
  datastoreDowntimeNotice: `Utilisez-vous la version classique du Datastore, y compris pendant
    <a href="https://iatistandard.org/en/news/technical-notice-2-iatis-datastore-to-be-integrated-in-new-unified-single-platform/">
    l’interruption du Datastore officiel de l’IITA</a>? Nous aimerions en savoir plus sur vous afin de nous permettre de mieux comprendre nos usagers et leurs besoins <br /> Contactez-nous à
    <a href="mailto:hello@codeforiati.org">hello@codeforiati.org</a>`,
  datastoreClassic: {
    heading: 'Le Datastore classique de l’IITA',
    strapline: "La version classique de l’IITA Datastore, renouvelé.",
  },
  accessText: 'Accédez à <code>{activities}</code> activités et <code>{transactions}</code> transactions.',
  viewDocumentation: 'Voir la documentation (en anglais)',
  viewAPI: "Voir l’API",
  health: {
    checkingDatastoreStatus: "Vérification des informations sur l’état du Datastore",
    datastoreOperational: 'Le Datastore est pleinement opérationnel',
    datastoreProblems: 'Le Datastore a des problèmes',
    lastUpdated: 'Dernière actualisation :',
    unknown: 'inconnu',
    queueData: `{itemsOnQueue} les jeux de données sont en attente de mise à jour, sur un total de {NumDatasets} jeux de données. Utilisez les données dès  présent ou patientez un instant que les mises à jour d'aujourd'hui soient disponibles.`,
    updatePctComplete: `Mise à jour quotidienne {parsingComplete}% complète.`,
    timing: {
      hoursAgo: 'il y a une heure | il y a {hours} heures',
      minutesAgo: 'il y a une minute | il y a {minutes} minutes',
      secondsAgo: 'il y a une seconde | il y a {seconds} secondes'
    }
  },
  getTheData: {
    heading: 'Obtenir les données',
    para1: 'Vous pouvez obtenir des données de IITA Datastore Classic dans différents formats.',
    para2: "Vous pouvez choisir de filtrer selon l'organisme qui publie, le lieu où se déroule l'activité et le secteur de l’activité. Vous pouvez choisir de télécharger des activités, des transactions ou des budgets.",
    chooseFilters: {
      heading: 'Choisir vos filtres',
      text: 'Ces options vous laissent filtrer les données IITA en fonction de ce que vous cherchez. Des filtres additionnels <a href="{baseURL}/docs/api/#filtering">sont disponibles</a> sur le serveur directement.'
    }
  },
  howToView: {
    heading: 'Comment souhaiteriez-vous visualiser cette information?',
    text: 'Ces options vous permettent de configurer la façon dont vos données sont désagrégées, rendant ainsi tous types d’analyse possibles.'
  },
  downloadData: {
    buttons: {
      download: 'Télécharger',
      reset: 'Réinitialiser',
    },
    yourLink: 'Votre lien :',
    copy: 'Copier',
    copied: 'Copié !'
  },
  footer: {
    sourceCode: '<a href="https://github.com/codeforIATI/iati-datastore">IATI Datastore Classic sur GitHub</a>, logiciel libre distribué sous la licence GNU Affero GPL v3.',
    credits: 'Le Datastore classique de l’IITA est un projet de <a href="https://codeforiati.org">Code for IATI</a>',
    privacyPolicy: 'Politique de confidentialité - en anglais'
  },
  outputFormat: {
    chooseFormat: 'Choisir le format',
    chooseSampleSize: {
      label: 'Choisir la taille de l’échantillon',
      options: [
        {
          'value': '1',
          'text': '1 ligne',
          'description': "Visualiser la sélection en n'incluant que la première ligne de données."
        },
        {
          'value': '50',
          'text': '50 lignes',
          'description': "Visualiser la sélection en incluant 50 lignes de données."
        },
        {
          'value': 'stream',
          'text': 'Sélection entière',
          'description': "Obtenir tous les résultats correspondant aux critères de recherche."
        }
      ]
    },
    csvOptions: {
      label: 'CSV Options',
      csvOnlyNote: 'Options disponibles seulement en format CSV.',
      chooseBreakdown: {
        label: 'Choisir le type de détail',
        options: [
          {
            'value': 'activity',
            'text': 'Une activité par ligne',
            'description': "Chaque ligne contient une activité unique. Les informations financières sont désagrégées. Les informations budgétaires sont exclues. Les autres champs potentiellement redondants (tels que les secteurs) sont publiés dans une case unique et délimités par un point virgule ."
          },
          {
            'value': 'transaction',
            'text': 'Une transaction par ligne',
            'description': 'Chaque ligne contient une transaction financière unique. L’identifiant de l’activité mère et les autres champs au niveau des activités sont répétés pour chaque activité. <br/> Si vous souhaitez analyser les activités financières par année, il faut sélectionner "Transactions" et calculer l’année de la transaction.'
          },
          {
            'value': 'budget',
            'text': 'Un budget par ligne',
            'description': "Chaque ligne continent une entrée pour la période budgétaire. Les données de transaction ne sont pas inclues. L'identifiant de l'activité mère et les autres champs au niveau des activités sont répétés pour chaque activité."
          }
        ],
      },
      repeatRows: {
        label: 'Reproduire les lignes',
        options: [
          {
            'value': '',
            'text': 'Non',
            'description': "L'information n'est pas désagrégée."
          },
          {
            'value': '/by_sector',
            'text': 'Extension multi-secteur',
            'description': "Chaque ligne Activité, Transaction ou Budget est reproduite pour chaque secteur publié séparémment. Le pourcentage correspondant à chaque division sectorielle est publié dans une colonne séparée. Cela vous permet d'ajouter facilement l'arithmétique à votre tableur pour calculer les valeurs proportionnelles."
          },
          {
            'value': '/by_country',
            'text': 'Extension multi-pays',
            'description': "Chaque ligne Activité, Transaction ou Budget est reproduite pour chaque pays publié séparémment. Le pourcentage correspondant à chaque division sectorielle est publié dans une colonne séparée. Cela vous permet d'ajouter facilement l'arithmétique à votre tableur pour calculer les valeurs proportionnelles."
          }
        ]
      }
    }
  },
  fields: {
    specificActivities: {
      label: 'Activités spécifiques',
      description: 'Chercher chaque activité spécifique en utilisant l’identifiant IITA, le Titre ou la Description.'
    },
    iatiIdentifier: {
      label: 'Identifiant de l’IITA',
      description: 'Chercher une activité avec un identifiant IITA spécifique (tel qu’un code projet).',
      placeholder: 'Tous les identifiants de l’IITA'
    },
    title: {
      label: 'Titre',
      description: 'Chercher les activités avec des titres qui incluent le text indiqué.',
      placeholder: 'Tous les titres'
    },
    description: {
      label: 'Description',
      description: 'Chercher les activités avec des descriptions qui incluent le text indiqué.',
      placeholder: 'Toutes les descriptions'
    },
    activityStatus: {
      label: "Statut de l’activité",
      description: 'Chercher les activités contenant seulement le statut de l’activité indiqué.',
      placeholder: 'Tous les types de statut de l’activité'
    },
    reportingOrganisation: {
      label: 'Organisme déclarant',
      description: 'L’organisme qui déclare les données est celui qui publie les données de l’IITA.',
      type: {
        label: 'Type d’organisme déclarant',
        description: 'Tous les types d’organisme déclarant',
        placeholder: 'Tous les types d’organisme déclarant'
      },
      ref: {
        label: 'Organisme déclarant',
        description: "Sélectionner seulement les données d'un organisme en particulier (ex: DFID)",
        placeholder: 'Tous les organismes déclarants'
      }
    },
    sector: {
      label: 'Secteur',
      description: 'Choisir le secteur ou les secteurs que vous cherchez.',
      placeholder: 'Tous les secteurs',
      note: 'Pour plus de détails sur les secteurs, voir la liste de codes <a href="https://codelists.codeforiati.org/fr/Sector" rel="noopener noreferrer" target="_blank">Secteur du CAD à 5 chiffres</a>.'
    },
    policyMarker: {
      label: 'Marqueur d’objectifs politiques',
      description: 'Un objectif politique ou thème abordé par l’activité, selon les marqueurs de l’OCDE CAD.',
      code: {
        label: 'Marqueur d’objectifs politiques',
        description: '',
        placeholder: 'Tous les marqueurs d’objectifs politiques'
      },
      significance: {
        label: 'Degré d’implication politique',
        placeholder: 'Tous les degrés d’implication politique'
      }
    },
    recipientLocation: {
      label: 'Pays ou région bénéficiaire',
      country: {
        label: 'Pays bénéficiaire',
        description: '',
        placeholder: 'Tous les pays beneficiaires'
      },
      region: {
        label: 'Région bénéficiaire',
        placeholder: 'Toutes les régions beneficiaires'
      },
      note: 'Choisir une région et un pays ne vont probablement pas fournir de données dans la mesure où la plupart des institutions qui publient le font soit pour une région soit pour un pays.'
    },
    dates: {
      label: 'Dates',
      startDateAfter: 'Date de début (après)',
      startDateBefore: 'Date de début (avant)',
      endDateAfter: 'Date de fin (après)',
      endDateBefore: 'Date de fin (avant)'
    }
  }
}
