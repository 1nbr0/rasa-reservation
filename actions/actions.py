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
      print("============")

      connection = psycopg2.connect(
        dbname="bqcxetmrbyw8gaxmsxix",
        user="uoj2kgme2r2ouqi2k9xw",
        password="xWslIJzcfmaYFoVX7XYLITLGIGEbn2",
        host="bqcxetmrbyw8gaxmsxix-postgresql.services.clever-cloud.com",
        port="50013",
      )
      cursor = connection.cursor()
      cursor.execute("SELECT SUM(nb_person) AS total_nb_person FROM rasa.booking WHERE date = %s;", (slot_date,))
      total_nb_person = cursor.fetchone()[0]

      if total_nb_person is not None:
        remaining_places = remaining_places - total_nb_person
      if((remaining_places - int(slot_nb_person)) < 0):
        dispatcher.utter_message(f"Nous disposons actuellement de {remaining_places} places disponibles. Souhaitez-vous choisir une nouvelle date ?")
        return [SlotSet("isAvailable", False)]

      dispatcher.utter_message(f"Nous avons suffisamment de places disponibles. Souhaitez-vous confirmer votre réservation ?")
      return [SlotSet("isAvailable", True)]

    except psycopg2.Error as e:
      dispatcher.utter_message("Error connecting to the database: {}".format(e))
      return [SlotSet("isAvailable", False)]

    finally:
      if 'connection' in locals():
          cursor.close()
          connection.close()

      return [SlotSet("story_number", False)]

class CreateBooking(Action):
  def name(self) -> Text:
    return "action_create_booking"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[SlotSet]:
    try:
      # Génération d'un code de réservation unique
      booking_code = str(uuid.uuid4())

      # Récupération des valeurs des slots
      slot_name = tracker.get_slot("slot_name")
      slot_nb_person = tracker.get_slot("slot_nb_person")
      slot_phone_nb = tracker.get_slot("slot_phone_nb")
      slot_date = datetime.strptime(tracker.get_slot("slot_date"), "%d/%m/%Y").strftime('%Y-%m-%d')
      slot_time = tracker.get_slot("slot_time")

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
      cursor.execute("INSERT INTO rasa.booking (booking_code, name, number_person, phone_number, date, time) VALUES (%s, %s, %s, %s, %s, %s);",
        (booking_code, slot_name, slot_nb_person, slot_phone_nb, slot_date, slot_time))
      connection.commit()

      dispatcher.utter_message(f"Votre réservation a été créée avec succès! Votre code de réservation est : {booking_code}")
      return [SlotSet("booking_created", True)]

    except psycopg2.Error as e:
      dispatcher.utter_message("Erreur lors de la création de la réservation: {}".format(e))
      return [SlotSet("booking_created", False)]

    finally:
      if 'connection' in locals():
        cursor.close()
        connection.close()

class DeleteBooking(Action):
  def name(self) -> Text:
    return "action_delete_booking"

  def run(self, dispatcher: CollectingDispatcher,
          tracker: Tracker,
          domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    try:
      # Connexion à la base de données
      connection = psycopg2.connect(
          dbname="votre_dbname",
          user="votre_utilisateur",
          password="votre_mot_de_passe",
          host="votre_host",
          port="votre_port"
      )
      cursor = connection.cursor()

      # Récupérer l'ID de la réservation à supprimer depuis les slots
      booking_id = tracker.get_slot("booking_id")

      # Supprimer la réservation en fonction de l'ID
      cursor.execute("DELETE FROM booking WHERE id = %s;", (booking_id,))
      connection.commit()

      # Envoyer un message de confirmation à l'utilisateur
      dispatcher.utter_message("La réservation a été supprimée avec succès.")

    except psycopg2.Error as e:
      dispatcher.utter_message("Erreur lors de la suppression de la réservation :", str(e))

    finally:
      # Fermer la connexion à la base de données
      if 'connection' in locals():
          cursor.close()
          connection.close()

    return []
