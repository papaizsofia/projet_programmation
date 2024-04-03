#-----------------------#
#   Import packages     #
#-----------------------#

import time
import datetime
import smtplib
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#-----------------------------------------------#
#       Définition des variables globales       #
#-----------------------------------------------#

mois_31jours = [1,3,5,7,8,10,12] 
mois_30jours = [4,6,9,11]

synonymes_match = ["match", "choc", "derby", "bataille", "rencontre"] 
synonymes_mythique = ["mythique", "légendaire", "au sommet", "célèbre", "historique"]

OF_lien = "https://onefootball.com/en"

Leagues_dict = {'Bundesliga': [[1,2,3],[4],[15,16,17]],
            'Ligue 1': [[1,2],[3],[15,16,17]],
            'Premier League': [[1,2,3],[4,5],[17,18,19]],
            'Serie A': [[1,2,3],[4],[17,18,19]],
            'LaLiga': [[1,2,3],[4],[17,18,19]]} 

Leagues_list = [
    ["/competition/premier-league-9", "Premier League", "England"],
    ["/competition/laliga-10", "LaLiga", "Spain"],
    ["/competition/serie-a-13", "Serie A", "Italy"],
    ["/competition/bundesliga-1", "Bundesliga", "Germany"],
    ["/competition/ligue-1-23", "Ligue 1", "France"]]

Classics = {'Bundesliga': [['Borussia Dortmund', 'Bayern Munich']],
            'Ligue 1': [['PSG', 'Marseille'],
                        ['Marseille', 'Lyon']],
            'Premier League': [['Manchester United', 'Manchester City'],
                           ['Manchester United',  'Liverpool'],
                           ['Arsenal', 'Tottenham Hotspur'],
                           ['Arsenal', 'Chelsea'],
                           ['Chelsea', 'Tottenham Hotspur'],
                           ['Liverpool', 'Everton']],
            'Serie A': [['Inter', 'Milan'],
                        ['Roma', 'Lazio'],
                        ['Inter', 'Juventus'],
                        ['Napoli', 'Roma'],
                        ['Napoli', 'Juventus']],
            'LaLiga': [['Real Madrid', 'Barcelona'],
                       ['Real Madrid', 'Atlético de Madrid'],
                       ['Sevilla', 'Real Betis'],
                       ['Athletic Club', 'Real Sociedad']]}

# Données des utilisateurs
donnees_utilisateurs = {
    'name': ['Dupont', 'Durand', 'Tremblay','Gomez'],
    'fname': ['Jean', 'Marie', 'Pierre','Louis'],
    'mail': ['adrien.bolmont@etu.unistra.fr', 'adrienbolmontempsai@gmail.com', 'adrienbolmont@gmail.com', 'lagl61549@gmail.com'],
    'Club': ['Sevilla', 'Mallorca', 'Barcelona', 'Inter']
}

df_user_data = pd.DataFrame(donnees_utilisateurs)

#-----------------------#
#   Driver adjustment   #
#-----------------------#

# Spécifiez le chemin d'accès au pilote du navigateur et le user
DRIVER_PATH = "C:/Users/Admin/Downloads/chromedriver-win64/chromedriver.exe"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

# Créer un objet Options
options = Options()
options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Spécifiez le chemin d'accès à l'exécutable de Chrome si nécessaire
options.add_argument(f'user-agent={user_agent}')
options.headless = True  # Pour exécuter Chrome en mode headless (sans interface graphique), décommentez cette ligne

#-----------------------------#
#   Création des fonctons     #
#-----------------------------#

def verification(jour, mois, annee):
    if not isinstance(jour, (int, float)) or not isinstance(mois, (int, float)) or not isinstance(annee, (int, float)):
       raise ValueError("Les paramètres doivent être des nombres.")
    if not annee > 2023:
        raise ValueError("La date n'est pas dans le bon format. (Année)")
    elif not 0 < mois < 13:
        raise ValueError("La date n'est pas dans le bon format. (Mois)")
    elif not 0 < jour < 32 and mois in mois_31jours:
        raise ValueError("La date n'est pas dans le bon format. (Jour)")
    elif not 0 < jour < 31 and mois in mois_30jours:
        raise ValueError("La date n'est pas dans le bon format. (Jour)")
    elif not 0 < jour < 29 and mois == 2 and annee%4 != 0:
        raise ValueError("La date n'est pas dans le bon format. (Jour)")
    elif not 0 < jour < 30 and mois == 2 and annee%4 == 0:
        raise ValueError("La date n'est pas dans le bon format. (Jour)")
    return "ok"

def games_link(jour, mois, annee):
    verif = verification(jour, mois, annee)
    if verif == "ok":
        jour = str(jour)
        mois = str(mois)
        annee = str(annee)
        
        if len(jour) == 1:
            jour = "0" + jour
        if len(mois) == 1:
            mois = "0" + mois
        
        lien_date = "/matches?date=" + annee + "-" + mois + "-" + jour
        return OF_lien + lien_date

def rankings():
    Rankings_leagues = {}
    for league in Leagues_list:
        # Open the link
        driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=options)
        driver.get(OF_lien + league[0] + "/table")
        
        time.sleep(5)
        
        try:
            click_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            click_button.click()
        except:
            pass  # If the button is not found or there's an error, ignore
        
        # Find the table element
        Ranking = driver.find_element(By.XPATH, "//*[@id='__next']/main/div/div/div[6]")
        table_text = Ranking.text
        
        Rankings_leagues[league[1]] = [table_text]
        
        
        String = Rankings_leagues[league[1]][0]
        values_String = String.split('\n')
        del values_String[:6]
        
        data_String = [values_String[i:i+8] for i in range(0, len(values_String), 8)]
        df_String = pd.DataFrame(data_String, columns=["Position", "Team", "Games", "Wins", "Draws", "Losses", "Goals", "Points"])
        Rankings_leagues[league[1]] = df_String
        
    driver.quit()
    return Rankings_leagues
    

def matchs(lien):
    Matchs = {}
    
    driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=options)
    driver.get(lien)

    time.sleep(5)

    try:
        click_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        click_button.click()
    except:
        pass

    for i in range(5, 12):
        xpath = "//*[@id='__next']/main/div/div/div[{0}]/div".format(i)
        matchs = driver.find_element(By.XPATH, xpath)
        Str = matchs.text
        values_Str = Str.split('\n')
        
        for league in Leagues_list:
            if values_Str[0] in league[1]:
            
                del values_Str[:3]
                del values_Str[-1]
            
                data_Str = [values_Str[i:i+4] for i in range(0, len(values_Str), 4)]
                df_Str = pd.DataFrame(data_Str, columns=["Home Team", "Away Team", "Date", "Time"])
                df_Str["League"] = league[1]

                Matchs[league[1]] = df_Str
            
    driver.quit()
    return Matchs

def classico(matchs_dict, classics):
    for league, matches_df in matchs_dict.items():
        matches_df['Classic'] = False
        for index, match in matches_df.iterrows():
            for classic in classics.get(league, []):
                if match["Home Team"] in classic and match["Away Team"] in classic:
                    matches_df.at[index, 'Classic'] = True
                    break

def position(matchs_dict, ranking, dict_league):
    for league, matches_df in matchs_dict.items():
        
        table = ranking.get(league)
        
        CL = dict_league.get(league)[0]
        EU = dict_league.get(league)[1]
        REG = dict_league.get(league)[2]
        
        matches_df['Championship'] = False
        matches_df['UEFA CL'] = False
        matches_df['UEFA EL'] = False
        matches_df['Relegation'] = False
        
        for index, match in matches_df.iterrows():
            Place_HT = table.index[table['Team'] == match['Home Team']].tolist()
            Place_HT = int(Place_HT[0])
            Place_AT = table.index[table['Team'] == match['Away Team']].tolist()
            Place_AT = int(Place_AT[0])
    
            for team in [Place_HT, Place_AT]:
                if team != 0 and abs(int(table['Points'][team]) - int(table['Points'][0])) < 4:
                    matches_df.at[index, 'Championship'] = True
                elif team == 0 and abs(int(table['Points'][1]) - int(table['Points'][0])) < 4:
                    matches_df.at[index, 'Championship'] = True

            for i in CL:
                if team != i and abs(int(table['Points'][team]) - int(table['Points'][i])) < 4:
                    matches_df.at[index, 'UEFA CL'] = True

            for i in EU:
                if team != i and abs(int(table['Points'][team]) - int(table['Points'][i])) < 4:
                    matches_df.at[index, 'UEFA EL'] = True
                
            for i in REG:
                if team != i and abs(int(table['Points'][team]) - int(table['Points'][i])) < 4:
                    matches_df.at[index, 'Relegation'] = True

def fav_team(team, matchs_dict):
    message = ""
    if team != "":
        for league, matches in matchs_dict.items():
            for index, row in matches.iterrows():
                if team == row['Home Team']:
                    message = f"\nBonne nouvelle ! Votre équipe, {row['Home Team']} joue le {row['Date']} contre {row['Away Team']}. \nLe match sera à {row['Time']}.\n Allez {row['Home Team']}!\n"
                    return message 
                elif team == row['Away Team']:
                    message = f"\nBonne nouvelle ! Votre équipe, {row['Away Team']} joue le {row['Date']} contre {row['Home Team']}. \nLe match sera à {row['Time']}.\n Allez {row['Away Team']}!\n"
                    return message
        return message
    else:
        return message          

def classic(matchs_dict):
    message = ""
    for league, matches in matchs_dict.items():
        for index, row in matches.iterrows():
            n = np.random.randint(1,5)
            if row["Classic"]:
                message += f"\n\nAlerte derby!\n{row['Home Team']} affronte {row['Away Team']} dans un {synonymes_match[n]} {synonymes_mythique[n]} de la {row['League']} le {row['Date']} à {row['Time']}."
                
    return message 


def autres_match(matchs_dict):
    messages = ""
    for league, matches in matchs_dict.items():
        
        for index, row in matches.iterrows():
            
            mess_champion = ""
            mess_CL = ""
            mess_EL = ""
            mess_releg = ""
            
            if row['Championship'] or row['UEFA CL'] or row['UEFA EL'] or row['Relegation']:
                messages += f"\n\n{league}:\n"
            
            if row['Championship']:
                mess_champion = f"\nMatch pour la première place : \n{row['Home Team']} vs {row['Away Team']} le {row['Date']} à {row['Time']}. \n"
                messages += mess_champion
                continue
        
            if row['UEFA CL']:
                mess_CL = f"\nPlace en Champions League en jeu : \n{row['Home Team']} vs {row['Away Team']} le {row['Date']} à {row['Time']}. \n"
                messages += mess_CL
                continue
        
            if row['UEFA EL']:
                mess_EL = f"\nPlace en Europa League en jeu : \n{row['Home Team']} vs {row['Away Team']} le {row['Date']} à {row['Time']}. \n"
                messages += mess_EL
                continue
        
            if row['Relegation']:
                mess_releg = f"\nMaintien en {row['League']} en jeu :\n{row['Home Team']} vs {row['Away Team']} le {row['Date']} à {row['Time']}. \n"
                messages += mess_releg 
        
    return messages 

def sujet_mail(phrase_fixe, date):
    date_string = date.strftime('%d-%m-%Y')
    return phrase_fixe + " " + date_string

def envoyer_email(destinataire_email, corps_mail, date):
    message = MIMEMultipart()
    expediteur_email = "pythontesting@laposte.net"
    message['From'] = expediteur_email
    message['To'] = destinataire_email
    message['Subject'] = sujet_mail(" Vos matchs du", date)
    message.attach(MIMEText(corps_mail, 'plain'))
    
    # Établir une connexion avec le serveur SMTP de Laposte
    serveur_smtp = smtplib.SMTP('smtp.laposte.net', 587)
    serveur_smtp.starttls()
    
    # Se connecter au compte expéditeur
    serveur_smtp.login(expediteur_email, "Nouveaumotdep@sse2024")
    
    # Envoyer l'e-mail
    serveur_smtp.send_message(message)
    
    # Fermer la connexion
    serveur_smtp.quit()

def corps_mail(User, matchs_dict, date):
    
    for index, row in User.iterrows():
        
        Message0 = f"Bonjour {row['fname']} \n\nVoici les matchs que nous vous conseillons le {date} :\n"
        Message1 = fav_team(row['Club'], matchs_dict)
        Message2 = classic(matchs_dict)
        Message3 = autres_match(matchs_dict)
        Message4 = "\n\nSalutations footbalistiques."
        
        Message_f = Message0 + Message1 + Message2 + Message3 + Message4
        
        envoyer_email(row['mail'], Message_f, date)
  
def projet(User, jour, mois, annee):
    global Classics
    global Leagues_dict
    Matchs = {}
    Rankings = {}
    date = datetime.date(annee, mois, jour)
    
    date1 = datetime.datetime(annee, mois, jour)
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    
    if date1 >= tomorrow:
        Rankings = rankings()
        Matchs = matchs(games_link(jour, mois, annee))
        classico(Matchs, Classics)
        position(Matchs,Rankings, Leagues_dict)
        corps_mail(User, Matchs, date)
        print("Mail envoyé!")
        
    else:
        print("Vous devez choisir une date à venir.")
#----------------------#
#   Foncton finale     #
#----------------------#

projet(df_user_data, 22, 5, 2024)
