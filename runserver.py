#!/usr/bin/env python

"""
Implements a Flask web application for Princeton University's
registrar system.
"""

import sys
import argparse
import sqlite3
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DATABASE = "reg.sqlite"


def string_handler(s):
    """
    Processes string input for SQL LIKE queries by escaping special
    characters. Converts empty/None strings to '%' wildcard and escapes
    SQL special characters to treat them as literal characters rather
    than wildcards.
    """
    if not s or s.strip() == "":
        return "%"
    s = s.replace("\\", "\\\\")
    s = s.replace("%", "\\%")
    s = s.replace("_", "\\_")
    return f"%{s}%"


@app.route("/")
@app.route("/index")
def index():
    """
    Serve the main HTML page for the registrar application.
    Returns Flask response object containing index.html
    """
    return send_file("index.html")


@app.route("/regoverviews")
def reg_overviews():
    """
    Handle API requests for class overview data, uses SQL
    joins to combine data from database tables, and returns
    a JSON response.
    """
    dept = string_handler(request.args.get("dept", ""))
    coursenum = string_handler(request.args.get("coursenum", ""))
    area = string_handler(request.args.get("area", ""))
    title = string_handler(request.args.get("title", ""))

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT cl.classid, cr.dept, cr.coursenum, c.title, c.area
            FROM classes cl
            JOIN courses c ON cl.courseid = c.courseid
            JOIN crosslistings cr ON c.courseid = cr.courseid
            WHERE cr.dept LIKE ? ESCAPE '\\'
            AND cr.coursenum LIKE ? ESCAPE '\\'
            AND c.area LIKE ? ESCAPE '\\'
            AND c.title LIKE ? ESCAPE '\\'
            ORDER BY cr.dept, cr.coursenum, cl.classid
        """

        cursor.execute(query, (dept, coursenum, area, title))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify([True, rows])

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return jsonify([False, "A server error occurred. "
                       "Please contact the system administrator."])
    except (ValueError, TypeError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        return jsonify([False, "A server error occurred. "
                       "Please contact the system administrator."])


@app.route("/regdetails")
def reg_details():
    """
    Handle API requests for detailed class information andreturns
    a JSON response. 
    """
    classid = request.args.get("classid", "")
    if classid == "":
        return jsonify([False, "missing classid"])

    try:
        classid = int(classid)
    except ValueError:
        return jsonify([False, "non-integer classid"])

    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT classid, days, starttime, endtime, bldg, roomnum, courseid
            FROM classes WHERE classid = ?
        """, (classid,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            return jsonify([False,
                           f"no class with classid {classid} exists"])

        class_info = dict(row)
        course_id = class_info["courseid"]

        cursor.execute("""
            SELECT area, title, descrip, prereqs
            FROM courses WHERE courseid = ?
        """, (course_id,))
        course_row = cursor.fetchone()
        if course_row:
            course_dict = dict(course_row)
            class_info["area"] = course_dict.get("area", "")
            class_info["title"] = course_dict.get("title", "")
            class_info["descrip"] = course_dict.get("descrip", "")
            class_info["prereqs"] = course_dict.get("prereqs", "")

        cursor.execute("""
            SELECT cr.dept, cr.coursenum
            FROM crosslistings cr
            WHERE cr.courseid = ?
            ORDER BY cr.dept, cr.coursenum
        """, (course_id,))
        crosslistings = cursor.fetchall()
        class_info["deptcoursenums"] = [
            {"dept": row["dept"], "coursenum": row["coursenum"]}
            for row in crosslistings
        ]

        cursor.execute("""
            SELECT p.profname
            FROM profs p
            JOIN coursesprofs cp ON p.profid = cp.profid
            WHERE cp.courseid = ?
            ORDER BY p.profname
        """, (course_id,))
        prof_rows = cursor.fetchall()
        class_info["profnames"] = [row["profname"] for row in prof_rows]

        conn.close()
        return jsonify([True, class_info])

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return jsonify([False, "A server error occurred. "
                       "Please contact the system administrator."])
    except (ValueError, TypeError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        return jsonify([False, "A server error occurred. "
                       "Please contact the system administrator."])


def main():
    """
    Parse command-line arguments and starts the Flask server.
    """
    parser = argparse.ArgumentParser(
        description="The registrar application")
    parser.add_argument(
        "port", type=int,
        help="the port at which the server should listen")
    args = parser.parse_args()
    app.run(host="0.0.0.0", port=args.port, debug=False)

if __name__ == "__main__":
    main()
