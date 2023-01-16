import json
from tqdm import tqdm
from percheron.utils import cache


DJANGO_TRAC = "https://code.djangoproject.com/jsonrpc"


def get_trac_details(ticket_no):
    """For a ticket number, get the ticket information and changes from Trac"""

    session = cache.session()
    ticket_comments = []

    # Shout out to rixx https://gist.github.com/rixx/422392d2aa580b5d286e585418bf6915
    resp = session.post(
        DJANGO_TRAC,
        data=json.dumps(
            {"method": "ticket.get", "id": ticket_no, "params": [ticket_no]}
        ),
        headers={"Content-Type": "application/json"},
    )

    data = resp.json()["result"][3]

    ticket = {
        "ticket_id": ticket_no,
        "status": data["status"],
        "reporter": data["reporter"],
        "resolution": data["resolution"],
        "description": data["description"],
    }

    # struct ticket.changeLog(int id, int when=0)
    # Return the changelog as a list of tuples of the form
    # (time, author, field, oldvalue, newvalue, permanent).
    response = session.post(
        DJANGO_TRAC,
        data=json.dumps(
            {"method": "ticket.changeLog", "id": ticket_no, "params": [ticket_no]}
        ),
        headers={"Content-Type": "application/json"},
    )

    changes = response.json()["result"]

    for change in changes:
        name = change[1]
        if name:
            name = name.split("<")[0].strip()  # remove emails,
        ticket_comments.append(
            {
                "ticket_id": ticket_no,
                "datetime": change[0]["__jsonclass__"][1],
                "name": name,
                "change_type": change[2],
                "old_value": change[3],
                "new_value": change[4],
            }
        )
    return ticket, ticket_comments


def get_trac_tickets(tickets):

    trac_tickets = []
    trac_ticket_comments = []

    for ticket_no in tqdm(tickets):
        ticket, ticket_comments = get_trac_details(ticket_no)
        trac_tickets.append(ticket)
        trac_ticket_comments += ticket_comments

    return trac_tickets, trac_ticket_comments
