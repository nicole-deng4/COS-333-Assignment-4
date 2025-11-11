import sys
import argparse
import sqlite3
from flask import Flask, request, jsonify, send_file

app = Flask (__name__)

database = "reg.sqlite"

def string_handler (s):
    if not s or s.strip() == "":
        return "%"
    s = s.replace("\\", "\\\\")
    s = s.replace("%", "\\%")
    s = s.replace("_", "\\_")
    return f"%{s}%"

@app.route("/")
@app.route("/index")
def index():
    return send_file("index.html")

@app.route("/regoverviews")
def reg_overviews():
    dept = string_handler(request.args.get("dept", ""))
    coursenum = string_handler(request.args.get("coursenum", ""))
    area = string_handler(request.args.get("area",""))
    title = string_handler(request.args.get("title", ""))

    try:
        conn = sqlite3.connect(database)
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
            ORDER BY cr.dept, cr.coursenum
        """
        
        cursor.execute(query, (dept, coursenum, area, title))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify (rows)
    
    except sqlite3.Error as e:
        print (f"Database error: {e}", file=sys.stderr)
        return jsonify ([False, "A server error occurred. Please contact the administrator"])
    except Exception as e:
        print (f"Unexpected error: {e}", file=sys.stderr)
        return jsonify ([False, "A server error occurred. Please contact the administrator"])
    
@app.route("/regdetails")
def reg_details():
    classid = request.args.get("classid", "")
    if classid == "":
        return jsonify ([False, "Missing classid parameter"])
    try:
        classid = int (classid)
    except ValueError:
        return jsonify ([False, "Non-integer classid parameter"])
    
    try:
        conn = sqlite3.connect (database)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT classid, days, starttime, endtime, bldg, roomnum, courseid
                       FROM classes where classid = ?
                       """, (classid))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            return jsonify ([False, f"No class with classid {classid} exists"])
        
        class_info = dict(row)
        course_id = class_info["courseid"]

        cursor.execute("""
                       SELECT area, title, description, prereqs 
                       FROM courses where courseid = ?
                       """, (course_id))
        course_info = cursors.fetchone()
        if course_info:
            class_info.update(dict(course_info))

        cursor.execute("""
                       SELECT p.profname
                       FROM profs p
                       JOIN courseprofs cp ON p.profid = cp.profid
                       WHERE cp.courseid = ?
                       ORDER BY p.profname pn
                       """, (course_id))
        class_info["profnames"] = [row["profname"] for row in cursor.fetchall()]
        conn.close()
        return jsonify (class_info)
    
    except sqlite3.Error as e:
        print (f"Database error: {e}", file=sys.stderr)
        return jsonify ([False, "A server error occurred. Please contact the administrator"])
    except Exception as e:
        print (f"Unexpected error: {e}", file=sys.stderr)
        return jsonify ([False, "A server error occurred. Please contact the administrator"])

def main ():
    parser = argparse.ArgumentParser (
        description = "The registrar application")
    parser.add_argument ("port", type = int, help = "the port number at which the server should listen")
    args = parser.parse_args()
    app.run(host = "0.0.0.0", port = args.port(), debug = False)

if __name__ == "__main__":
    main()