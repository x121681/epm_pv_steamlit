import csv

class PVEngine:
    """
    PV Responsibilities Engine with level-based filtering (L0–L4)
    """

    # ---------------------------------------------------------
    # LEVEL DEFINITIONS
    # ---------------------------------------------------------
    LEVELS = {
        "L0": 0,
        "L1": 1,
        "L2": 2,
        "L3": 3,
        "L4": 4,
    }

    # Minimum level required per process
    PROCESS_MIN_LEVEL = {
        "Lifecyclemanagement": 2,
        "Produktmanagement": 2,
        "Incident Management": 2,
        "Problem Management": 2,
        "Change Management": 2,
        "Releasemanagement": 3,
        "Business-Continuity-Management": 3,
        "Informationssicherheits- und Informationsrisikomanagement": 3,
        "Compliance": 3,
        "Softwareentwicklungsprozess": 3,
        "Einführung und Dokumentation": 1,
        "Asset-, Vertrags- und Lizenzmanagement (in Zusammenarbeit mit dem zentralen AVL-Management)": 2,
    }

    def __init__(self, csv_path="components/pv_journey.csv"):
        self.csv_path = csv_path
        self.tasks = self.load_tasks()

    # ---------------------------------------------------------
    # 1) CSV LOADING
    # ---------------------------------------------------------
    def load_tasks(self):
        tasks = []
        with open(self.csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=';')

            # Normalize headers
            normalized_fieldnames = {
                h: h.strip().lower().replace(" ", "_").replace(".", "")
                for h in reader.fieldnames
            }

            for row in reader:
                row = {normalized_fieldnames[k]: v.strip() for k, v in row.items()}

                # Split and normalize 'relevanz'
                raw_relevance = row.get("relevanz", "")
                relevanz_list = []
                for r in raw_relevance.split(","):
                    r = r.strip()
                    if r == "Eigenentw.":
                        relevanz_list.append("Eigenentwicklung")
                    elif r in ["Fremdsoftware", "Hardware"]:
                        relevanz_list.append(r)
                    # ignore empty or unknown

                tasks.append({
                    "pv": row["pv"],
                    "aufgabe": row["aufgabe"],
                    "häufigkeit": row["häufigkeit"],
                    "prozess": row["prozess"],
                    "relevanz": relevanz_list,
                })

        return tasks
   


    # ---------------------------------------------------------
    # 2) PRODUCT TYPE FILTERING (using relevanz)
    # ---------------------------------------------------------
    def filter_by_product_type(self, tasks, product_type):
        if product_type not in ["Fremdsoftware", "Eigenentwicklung", "Hardware"]:
            raise ValueError(f"Invalid product_type: {product_type}")

        return [t for t in tasks if product_type in t["relevanz"]]

    # ---------------------------------------------------------
    # 3) SCENARIO FILTERING
    # ---------------------------------------------------------
    def filter_by_scenario(self, tasks, scenario):
        SCENARIO_MAP = {
            "Neueinführung": [
                "Lifecyclemanagement",
                "Produktmanagement",
                "Einführung und Dokumentation",
            ],
            "Maintenance": [
                "Incident Management",
                "Problem Management",
                "Change Management",
            ],
            "Incident": ["Incident Management"],
            "Security relevant": [
                "Informationssicherheits- und Informationsrisikomanagement"
            ],
            "Release Upgrade": [
                "Releasemanagement",
                "Change Management",
            ],
        }

        allowed_processes = SCENARIO_MAP.get(scenario)
        if not allowed_processes:
            return tasks

        return [t for t in tasks if t["prozess"] in allowed_processes]

    # ---------------------------------------------------------
    # 4) LEVEL FILTERING
    # ---------------------------------------------------------
    def filter_by_level(self, tasks, level):
        if level not in self.LEVELS:
            raise ValueError(f"Invalid level: {level}")

        level_value = self.LEVELS[level]
        return [t for t in tasks if level_value >= self.PROCESS_MIN_LEVEL.get(t["prozess"], 0)]

    # ---------------------------------------------------------
    # 5) HIGH-LEVEL ENTRY FUNCTION
    # ---------------------------------------------------------
    def get_pv_responsibilities(self, product_type, scenario, level="L2"):
        result = self.filter_by_product_type(self.tasks, product_type)
        result = self.filter_by_scenario(result, scenario)
        result = self.filter_by_level(result, level)
        return sorted(result, key=lambda x: x["prozess"])

    # ---------------------------------------------------------
    # 6) UTILITIES
    # ---------------------------------------------------------
    def group_by_process(self, tasks):
        grouped = {}
        for t in tasks:
            grouped.setdefault(t["prozess"], []).append(t)
        return grouped

    def group_by_frequency(self, tasks):
        grouped = {}
        for t in tasks:
            grouped.setdefault(t["häufigkeit"], []).append(t)
        return grouped
