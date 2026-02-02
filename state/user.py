USERS = {
    "john.doe": {
        "password": "demo123",
        "roles": ["user"],
        "systems": ["device", "scanner"],
        "department": "IS-G",
    },
    "alice.admin": {
        "password": "admin123",
        "roles": ["admin"],
        "systems": ["device", "scanner", "epm"],
        "department": "IS-P",
    },
    "bob.epm": {
        "password": "epm123",
        "roles": ["user"],
        "systems": ["epm", "device"],
        "department": "CSO-I",
    },
}

PV_USERS = {
    "john.doe": {
        "display_name": "John Doe",
        "pv_roles": ["PV_TECHNISCH"],
        "domains": ["Security", "Infrastructure"],
        "active": True
    },
    "alice.admin": {
        "display_name": "Alice Admin",
        "pv_roles": ["PV_FACHLICH"],
        "domains": ["Business Applications"],
        "active": True
    },
    "bob.epm": {
        "display_name": "Bob Epm",
        "pv_roles": ["PV_TECHNISCH"],
        "domains": ["Network", "Data Management"],
        "active": True
    },
    "max.mustermann": {
        "display_name": "Max Mustermann",
        "pv_roles": ["PV_FACHLICH"],
        "domains": ["Finance", "ERP"],
        "active": True
    },
}
