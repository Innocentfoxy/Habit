import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app
import uuid

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

    # Get all habits from track collection
    habits = list(current_app.track_collection.find(
        {"type": "habit", "added": {"$lte": selected_date}}
    ))

    # Get completions for the selected date from track collection
    completions = [
        habit["habit_id"] 
        for habit in current_app.track_collection.find(
            {"type": "completion", "date": selected_date}
        )
    ]

    return render_template("index.html",
        habits=habits,
        selected_date=selected_date,
        title='Habit Tracker - Home',
        completions=completions)

@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    if request.method == "POST":
        habit_name = request.form.get("habitName")
        print(f"Received habit name: {habit_name}")  # Debug print
        
        if habit_name:
            # Create a new habit document in track collection
            habit_doc = {
                "_id": uuid.uuid4().hex,
                "type": "habit",
                "added": today,
                "name": habit_name,
                "created_at": datetime.datetime.now()
            }
            result = current_app.track_collection.insert_one(habit_doc)
            print(f"Inserted with ID: {result.inserted_id}")  # Debug print
            return redirect(url_for("pages.index"))
    
    return render_template("add_habit.html", 
                         title="Habit tracker - add habit", 
                         selected_date=today)

@pages.route("/complete", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit_id = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)
    
    # Create a completion document in track collection
    completion_doc = {
        "_id": uuid.uuid4().hex,
        "type": "completion",
        "habit_id": habit_id,
        "date": date,
        "completed_at": datetime.datetime.now()
    }
    current_app.track_collection.insert_one(completion_doc)
    
    return redirect(url_for("pages.index", date=date_string))

# Optional: Add a route to view all tracked data
@pages.route("/track")
def view_track():
    # Get all documents from track collection
    all_tracks = list(current_app.track_collection.find())
    
    # Separate habits and completions
    habits = [doc for doc in all_tracks if doc.get("type") == "habit"]
    completions = [doc for doc in all_tracks if doc.get("type") == "completion"]
    
    return render_template("track.html",
                         habits=habits,
                         completions=completions,
                         title="Track Collection Data")

# Optional: Add a route to clear track collection (for testing)
@pages.route("/clear-track")
def clear_track():
    current_app.track_collection.delete_many({})
    return redirect(url_for("pages.view_track"))

# Test route to verify database connection
@pages.route("/test-db")
def test_db():
    try:
        # Try to insert a test document
        test_doc = {
            "_id": "test_" + uuid.uuid4().hex,
            "type": "test",
            "message": "Database is working!",
            "timestamp": datetime.datetime.now()
        }
        result = current_app.track_collection.insert_one(test_doc)
        
        # Count documents
        count = current_app.track_collection.count_documents({})
        
        return f"Database working! Inserted test doc: {result.inserted_id}<br>Total documents: {count}"
    except Exception as e:
        return f"Database error: {str(e)}"