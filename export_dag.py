# Note: the module name is psycopg, not psycopg3
import psycopg
import CourseGraph

# Recursively collapses the given reqs into a single set.
# Disregards the and/or relationships.
# {'type': 'and', 'values': [
# {'type': 'or', 'values': [
#   {'classId': '2810', 'subject': 'CS'}, 
#   {'classId': '2331', 'subject': 'MATH'}
# ]}, 
# {'classId': '3500', 'subject': 'CS'}
# ]}
def extract_reqs(reqs: dict, set_in: set):
    for value in reqs["values"]:
        try:
            if "type" in value.keys():
                extract_reqs(value, set_in)
            else:
                set_in.add((value["subject"], value["classId"]))
        except AttributeError as e:
            print("problem extracting keys from value: {}".format(value))
    return set_in

# Connect to an existing database
if __name__ == "__main__":
    graph = CourseGraph.DependencyGraph()

    with psycopg.connect("dbname=searchneu_dev user=postgres host=localhost port=5432 password=default_password") as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            # Query the database and obtain data as Python objects.
            cur.execute("SELECT subject, class_id, coreqs, prereqs, name FROM courses")

            for record in cur:
                node_class = graph.add_class(record[0], record[1])
                node_class.set_course_name(record[4])

                coreqs = record[2]
                prereqs = record[3]

                if(len(coreqs["values"])):
                    coreqs_set = set()
                    extract_reqs(coreqs, coreqs_set)
                    #print("CoReqs: {}".format(coreqs_set))
                    for coreq in coreqs_set:
                        graph.add_corequisite(record[0], record[1], coreq[0], coreq[1])
                if(len(prereqs["values"])):
                    prereqs_set = set()
                    extract_reqs(prereqs, prereqs_set)
                    #print("PreReqs: {}".format(prereqs_set))
                    for prereq in prereqs_set:
                        graph.add_prerequisite(record[0], record[1], prereq[0], prereq[1])


    graph.export_dot_file("/Users/andrew/Projects/search_neu_experiments/output", "CS", ["CS"])
    graph.export_dot_file("/Users/andrew/Projects/search_neu_experiments/output", "Business", ["ACCT", "FINA", "MKTG", "MISM", "SCHM", "ORGB", "STRT", "INTB", "MGSC"])