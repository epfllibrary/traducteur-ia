# Publier une release et proposer un téléchargement direct

## Principe retenu

Une release GitLab associe un tag, des notes de version et un lien vers `traducteur-setup.exe`. Le projet suit déjà ce binaire dans Git : le lien de la release peut donc pointer vers le fichier brut du **tag**, sans nouvel hébergement ni runner CI.

Le projet est public et ne comportait aucune release au moment de préparer 1.2.0. Le premier lien `latest` deviendra utilisable après la publication d'une release comportant l'asset décrit ci-dessous. D'ici là, le [téléchargement direct du dépôt](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/raw/main/bin/traducteur-setup.exe?inline=false) fonctionne indépendamment des releases.

Les archives ZIP et TAR automatiquement générées par GitLab contiennent les sources ; elles ne remplacent pas le setup Windows.

## Préparer la version

1. Aligner la version de l'application, de l'installateur, du README et des scripts. Pour cette publication : `1.2.0`, version Windows `1.2.0.0`, tag `v1.2.0`.
2. Mettre à jour le changelog, les guides et la capture d'écran.
3. Exécuter les tests et reconstruire l'exécutable puis le setup avec les scripts Windows.
4. Tester le setup et les fonctions concernées.
5. Exécuter depuis la racine du dépôt :

```bash
python scripts/prepare_release.py
```

Cette commande écrit `build/release/v1.2.0/release.json` et `release-notes.md`, avec l'empreinte SHA-256 du setup construit. Elle ne crée aucun commit, tag ou objet distant. Relire ces fichiers avant publication.

## Enregistrer et pousser la version validée

Après validation du contenu et du setup, enregistrer les modifications et `bin/traducteur-setup.exe`, puis créer le tag sur ce commit. Les commandes suivantes décrivent l'étape de publication ; elles ne font pas partie de la préparation locale :

```bash
git commit -m "Release 1.2.0"
git tag -a v1.2.0 -m "Traducteur 1.2.0"
git push origin main
git push origin v1.2.0
```

Sélectionner les fichiers à inclure avec `git add` et vérifier le diff indexé avant le commit. Le tag doit contenir le setup reconstruit. Ne pas déplacer un tag déjà publié.

## Créer la release GitLab

Depuis [les releases du projet](https://gitlab.epfl.ch/sisb-public/id/traducteur/-/releases), créer une release pour le tag existant `v1.2.0`, intitulée **Traducteur 1.2.0**, et reprendre les notes générées. Ajouter cet asset :

| Champ | Valeur |
| --- | --- |
| Nom | Installateur Windows — Traducteur 1.2.0 |
| URL | `https://gitlab.epfl.ch/sisb-public/id/traducteur/-/raw/v1.2.0/bin/traducteur-setup.exe?inline=false` |
| Type | `package` |
| Chemin direct | `/traducteur-setup.exe` |

Le chemin direct est nécessaire pour obtenir le lien permanent. Il peut être défini via l'API avec `direct_asset_path`. Le JSON généré contient déjà cet asset et les notes de version. Une autre méthode de publication, après authentification avec un jeton GitLab doté du droit `api`, est :

```bash
curl --fail-with-body --request POST \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --header "Content-Type: application/json" \
  --data-binary @build/release/v1.2.0/release.json \
  "https://gitlab.epfl.ch/api/v4/projects/40498/releases"
```

Cette commande **publie** la release et nécessite le tag déjà poussé. Elle doit être exécutée une seule fois pour cette version. Ne pas enregistrer le jeton dans le dépôt ou le JSON de publication.

## Liens de téléchargement

Après publication, vérifier anonymement ces deux liens, en suivant les redirections et en comparant le SHA-256 au setup local :

- Version précise : `https://gitlab.epfl.ch/sisb-public/id/traducteur/-/releases/v1.2.0/downloads/traducteur-setup.exe`
- Dernière release : `https://gitlab.epfl.ch/sisb-public/id/traducteur/-/releases/permalink/latest/downloads/traducteur-setup.exe`

Le second lien peut alors remplacer le téléchargement direct depuis `main` dans le README et les guides de déploiement. Conserver le même chemin d'asset aux releases suivantes pour garder cette adresse stable. Une release publiée doit toujours cibler le fichier de son tag, pas celui de `main`.

## Évolution possible

Si le poids des binaires dans l'historique Git devient gênant, le Generic Package Registry de GitLab peut héberger les prochains setups ; le lien permanent de release pourra continuer à les désigner. Cette migration n'est pas nécessaire pour la première release.

Références : [champs et liens permanents des releases](https://docs.gitlab.com/user/project/releases/release_fields/), [API de création d'une release](https://docs.gitlab.com/api/releases/#create-a-release), [Generic Package Registry](https://docs.gitlab.com/user/packages/generic_packages/).
