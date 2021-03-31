# pylint: skip-file
registration_desc = """
Sends the event registration form to the events database
"""

registration_summ = """
Register event
"""

events_by_location_desc = """
Take in a user's location and a given mile radius and return all the events within that radius
"""
events_by_location_summ = """
Get events within a given radius
"""

get_event_desc = """
Returns an event with a matching event ID
"""
get_event_summ = """
Get event by ID
"""

get_event_by_status_desc = """
Returns an event with matching event ID and matching status tag enum
"""
get_event_by_status_summ = """
Get event by ID and status
"""

get_all_events_desc = """
Returns all of the events in the database
"""
get_all_events_summ = """
Get all events
"""

delete_event_desc= """
Changes enum flag of event to "deleted"
"""
delete_event_summ = """
'Deletes' or cancels an event
"""