# NEU Course DAG Exporter

## Setup:
1. Setup the backend as described in the backend docs: https://apidocs.searchneu.com/#/getting-started/running
   1. Make sure to use the cache as described
   2. The two relevant github repos are as follows. Both will be necessary (if using cache)
      1. https://github.com/sandboxnu/course-catalog-api.git
      2. https://github.com/sandboxnu/course-catalog-api-cache.git
2. Install python dependencies
   1. `pip install pydot psycopg`
3. Install graphviz dependency. This is necessary for exporting dot files to PNG.
   1. `brew install graphviz`
4. Run the `export_dag.py` script. The script can be modified to generate different versions of the graph to allow/remove specific subjects.

The script works by querying all courses in the postgresql database and building and building up a dependency graph with pre-reqs and co-reqs. 
Once the graph has been constructed, we export the results to a dot file. We also export a visualized version using graphviz. Only 
courses that fall under target course names will be exported in the graph, however, we will traverse the dependency graph to include
non-target courses if they are dependencies. For example, if we ask to only export CS classes, but the CS class has a dependency on 
some math classes, the math classes will be included in the export.

## Correctness
To simplify the graph structure there are some inaccuracies in the rendered graph. The actual pre-reqs of courses
is modeled using `or` and `and` relationships. For example, you could have the following graph.
```
course 1 ---> course 2.1 AND course 2.2
         |
         or
         |
         ---> course 3.1 AND course 3.2
```
These statements can nest down multiple levels.

To simplify the representation in the overall graph, we break this apart and represent all possible branches as required.
Therefore, the pre-reqs shown are an OVER estimate of the actual required pre-reqs.

```
course 1 ---> course 2.1 AND course 2.2 AND course 3.1 AND course 3.2
```

## DB
Some DB Schema dumped from Postgres.

```
searchneu_dev=# \d
                 List of relations
 Schema |        Name        |   Type   |  Owner   
--------+--------------------+----------+----------
 public | _prisma_migrations | table    | postgres
 public | courses            | table    | postgres
 public | followed_courses   | table    | postgres
 public | followed_sections  | table    | postgres
 public | majors             | table    | postgres
 public | professors         | table    | postgres
 public | sections           | table    | postgres
 public | subjects           | table    | postgres
 public | term_ids           | table    | postgres
 public | test               | table    | postgres
 public | test_id_seq        | sequence | postgres
 public | users              | table    | postgres
 public | users_id_seq       | sequence | postgres
(13 rows)

searchneu_dev=# \d+ courses
                                                        Table "public.courses"
      Column      |              Type              | Collation | Nullable |      Default      | Storage  | Stats target | Description 
------------------+--------------------------------+-----------+----------+-------------------+----------+--------------+-------------
 class_attributes | text[]                         |           |          |                   | extended |              | 
 class_id         | text                           |           |          |                   | extended |              | 
 coreqs           | jsonb                          |           |          |                   | extended |              | 
 description      | text                           |           |          |                   | extended |              | 
 fee_amount       | integer                        |           |          |                   | plain    |              | 
 fee_description  | text                           |           |          |                   | extended |              | 
 host             | text                           |           |          |                   | extended |              | 
 id               | text                           |           | not null |                   | extended |              | 
 last_update_time | timestamp(3) without time zone |           |          | CURRENT_TIMESTAMP | plain    |              | 
 max_credits      | integer                        |           |          |                   | plain    |              | 
 min_credits      | integer                        |           |          |                   | plain    |              | 
 name             | text                           |           |          |                   | extended |              | 
 nupath           | text[]                         |           |          |                   | extended |              | 
 opt_prereqs_for  | jsonb                          |           |          |                   | extended |              | 
 prereqs          | jsonb                          |           |          |                   | extended |              | 
 prereqs_for      | jsonb                          |           |          |                   | extended |              | 
 pretty_url       | text                           |           |          |                   | extended |              | 
 subject          | text                           |           |          |                   | extended |              | 
 term_id          | text                           |           |          |                   | extended |              | 
 url              | text                           |           |          |                   | extended |              | 
Indexes:
    "courses_pkey" PRIMARY KEY, btree (id)
    "uniqueCourseProps" UNIQUE, btree (class_id, term_id, subject)
Referenced by:
    TABLE "followed_courses" CONSTRAINT "followed_courses_course_hash_fkey" FOREIGN KEY (course_hash) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE
    TABLE "sections" CONSTRAINT "sections_class_hash_fkey" FOREIGN KEY (class_hash) REFERENCES courses(id) ON UPDATE CASCADE ON DELETE CASCADE
```