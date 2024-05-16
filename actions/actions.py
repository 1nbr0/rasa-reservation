from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import psycopg2
from datetime import datetime
import uuid

class CheckIsAvailable(Action):
  def name(self) -> Text:
    return "action_check_is_available"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[SlotSet]:
    try:
      remaining_places = 30
      slot_nb_person = tracker.get_slot("slot_nb_person")
      slot_date = datetime.strptime(tracker.get_slot("slot_date"), "%d/%m/%Y").strftime('%Y-%m-%d')

      print(slot_nb_person)
      print(slot_date)

      connection = psycopg2.connect(
        dbname="bqcxetmrbyw8gaxmsxix",
        user="uoj2kgme2r2ouqi2k9xw",
        password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
        host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
        port="50013",
      )
      cursor = connection.cursor()
      cursor.execute("SELECT SUM(number_person) AS total_number_person FROM rasa.booking WHERE date = %s;", (slot_date,))
      total_nb_person = cursor.fetchone()[0]

      if total_nb_person is not None:
        remaining_places = remaining_places - total_nb_person
      if((remaining_places - int(slot_nb_person)) < 0):
        dispatcher.utter_message(f"Nous disposons actuellement de {remaining_places} places disponibles. Souhaitez-vous choisir une nouvelle date ?")
        return [SlotSet("isAvailable", False)]

      dispatcher.utter_message(f"Nous avons suffisamment de places disponibles. Renseigner un nom pour continuer la réservation.")
      return [SlotSet("isAvailable", True)]

    except psycopg2.Error as e:
      dispatcher.utter_message("Error connecting to the database: {}".format(e))
      return [SlotSet("isAvailable", False)]

    finally:
      if 'connection' in locals():
          cursor.close()
          connection.close()

class CreateBooking(Action):
  def name(self) -> Text:
    return "action_create_booking"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Génération d'un code de réservation unique
      booking_code = str(uuid.uuid4())

      # Récupération des valeurs des slots
      slot_name = tracker.get_slot("slot_name")
      slot_nb_person = tracker.get_slot("slot_nb_person")
      slot_phone_nb = tracker.get_slot("slot_phone_nb")
      slot_date = datetime.strptime(tracker.get_slot("slot_date"), "%d/%m/%Y").strftime('%Y-%m-%d')
      slot_time = tracker.get_slot("slot_time")
      slot_commentary = tracker.get_slot("slot_commentary")

      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="bqcxetmrbyw8gaxmsxix",
          user="uoj2kgme2r2ouqi2k9xw",
          password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
          host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
          port="50013"
      )
      cursor = connection.cursor()

      # Insertion des données dans la base de données
      cursor.execute("INSERT INTO rasa.booking (booking_code, name, number_person, phone_number, date, time, commentary) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (booking_code, slot_name, slot_nb_person, slot_phone_nb, slot_date, slot_time, slot_commentary))
      connection.commit()

      dispatcher.utter_message(f"Votre réservation a été créée avec succès! Votre code de réservation est : {booking_code} \n\nVeuillez garder ce numéro précieusement.\nIl vous sera demandé de le renseigner si vous souhaitez obtenir des infos ou annuler votre réservation.")
      dispatcher.utter_message(f"\n\nPour résumer, vous souhaitez réserver une table pour le {slot_date} à {slot_time} pour {slot_nb_person} au nom de {slot_name}. \nVotre numéro de téléphone est {slot_phone_nb}.")
      return [SlotSet("booking_created", True)]

    except psycopg2.Error as e:
      dispatcher.utter_message("Erreur lors de la création de la réservation: {}".format(e))
      return [SlotSet("booking_created", False)]

    finally:
      if 'connection' in locals():
        cursor.close()
        connection.close()

class CheckBookingCode(Action):
  def name(self) -> Text:
    return "action_check_booking_code"

  def run(self, dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="bqcxetmrbyw8gaxmsxix",
          user="uoj2kgme2r2ouqi2k9xw",
          password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
          host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
          port="50013"
      )
      cursor = connection.cursor()

      # Récupérer l'ID de la réservation à vérifier depuis les slots
      booking_code = tracker.get_slot("slot_booking_code")

      # Vérifier l'existence de la réservation
      cursor.execute("SELECT 1 FROM rasa.booking WHERE booking_code = %s;", (booking_code,))
      result = cursor.fetchone()

      if result:
        return [SlotSet("isBookingExist", True)]
      else:
        dispatcher.utter_message("Le code de réservation est invalide.")
        return [SlotSet("isBookingExist", False)]

    except psycopg2.Error as e:
      dispatcher.utter_message("Erreur lors de la vérification du code de réservation :", str(e))

    finally:
      # Fermer la connexion à la base de données
      if 'connection' in locals():
          cursor.close()
          connection.close()

    return [SlotSet("isBookingExist", False)]

class DeleteBooking(Action):
  def name(self) -> Text:
    return "action_delete_booking"

  def run(self, dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Vérifier si la réservation existe
      booking_exists = tracker.get_slot("isBookingExist")
      if not booking_exists:
        dispatcher.utter_message("La réservation n'existe pas.")
        return []

      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="bqcxetmrbyw8gaxmsxix",
          user="uoj2kgme2r2ouqi2k9xw",
          password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
          host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
          port="50013"
      )
      cursor = connection.cursor()

      # Récupérer l'ID de la réservation à supprimer depuis les slots
      booking_code = tracker.get_slot("slot_booking_code")

      # Supprimer la réservation en fonction de booking_code
      cursor.execute("DELETE FROM rasa.booking WHERE booking_code = %s;", (booking_code,))
      connection.commit()

      # Envoyer un message de confirmation à l'utilisateur
      dispatcher.utter_message("La réservation a été annulée avec succès.")

    except psycopg2.Error as e:
      dispatcher.utter_message("Erreur lors de l'annulation de la réservation :", str(e))

    finally:
      # Fermer la connexion à la base de données
      if 'connection' in locals():
          cursor.close()
          connection.close()

    return []

class UpdateCommentary(Action):
  def name(self) -> Text:
    return "action_update_booking_commentary"

  def run(self, dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="bqcxetmrbyw8gaxmsxix",
          user="uoj2kgme2r2ouqi2k9xw",
          password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
          host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
          port="50013"
      )
      cursor = connection.cursor()

      # Récupérer l'ID de la réservation et le nouveau commentaire depuis les slots
      booking_code = tracker.get_slot("slot_booking_code")
      new_commentary = tracker.get_slot("slot_commentary")
      print(booking_code)
      print(new_commentary)

      # Mettre à jour le commentaire de la réservation
      cursor.execute("UPDATE rasa.booking SET commentary = %s WHERE booking_code = %s;", (new_commentary, booking_code))
      connection.commit()

      # Envoyer un message de confirmation à l'utilisateur
      dispatcher.utter_message("Le commentaire de votre réservation a été mis à jour avec succès.")

    except psycopg2.Error as e:
      dispatcher.utter_message(f"Erreur lors de la mise à jour du commentaire de la réservation : {str(e)}")

    finally:
      # Fermer la connexion à la base de données
      if 'connection' in locals():
        cursor.close()
        connection.close()

    return []

class GetBookingInfo(Action):
  def name(self) -> Text:
    return "action_get_booking_info"

  def run(self, dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="bqcxetmrbyw8gaxmsxix",
          user="uoj2kgme2r2ouqi2k9xw",
          password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
          host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
          port="50013"
      )
      cursor = connection.cursor()

      # Récupérer le code de réservation depuis les slots
      booking_code = tracker.get_slot("slot_booking_code")

      # Rechercher les informations de la réservation en fonction du booking_code
      cursor.execute("SELECT name, phone_number, number_person, date, time, commentary FROM rasa.booking WHERE booking_code = %s;", (booking_code,))
      booking_info = cursor.fetchone()

      if booking_info:
        name, phone_number, number_person, date, time, commentary = booking_info
        response = (f"Les détails de votre réservation sont les suivants :\n"
                    f"Nom : {name}\n"
                    f"Numéro de téléphone : {phone_number}\n"
                    f"Nombre de personnes : {number_person}\n"
                    f"Date : {date}\n"
                    f"Heure : {time}\n"
                    f"Commentaire : {commentary}")
        dispatcher.utter_message(response)
        dispatcher.utter_message("\nVoulez-vous modifier le commentaire ? (oui/non)")
      else:
        dispatcher.utter_message("Aucune réservation trouvée avec le code fourni.\n \nVeuillez re saisir le code de réservation, s'il vous plaît.")

    except psycopg2.Error as e:
      dispatcher.utter_message(f"Erreur lors de la récupération des informations de réservation : {str(e)}")

    finally:
      # Fermer la connexion à la base de données
      if 'connection' in locals():
          cursor.close()
          connection.close()

    return []