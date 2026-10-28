import sqlite3
from io import BytesIO

import streamlit as st
from gtts import gTTS

DB_PATH = "books_en.db"
LEVELS = ["Beginner", "Intermediate", "Advanced"]

SEED_BOOKS = [
    ("The Little Prince", "Antoine de Saint-Exupery", "Novel", 8, "Beginner",
     "A pilot stranded in the desert meets a young prince from a distant planet who talks about friendship, love and what really matters in life."),
    ("The Old Man and the Sea", "Ernest Hemingway", "Novel", 12, "Beginner",
     "An old fisherman fights a long battle at sea against a giant fish, in a story about patience and dignity."),
    ("Animal Farm", "George Orwell", "Novel", 13, "Beginner",
     "Farm animals rebel against their owner to rule themselves, but the revolution slowly turns into a harsher tyranny."),
    ("1984", "George Orwell", "Novel", 16, "Intermediate",
     "A society watched by an all-powerful government at every moment, and a man who tries to keep his freedom of thought."),
    ("The Alchemist", "Paulo Coelho", "Novel", 14, "Beginner",
     "A young shepherd travels from Spain to Egypt in search of treasure and learns the meaning of following a dream."),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Novel", 18, "Advanced",
     "A poor student commits a murder and then suffers an intense inner struggle between guilt and justification."),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Novel", 18, "Advanced",
     "The saga of the Buendia family across seven generations in the town of Macondo, mixing reality with magic."),
    ("Frankenstein in Baghdad", "Ahmed Saadawi", "Novel", 18, "Intermediate",
     "An Iraqi novel about a man who stitches together the remains of bombing victims into one body that comes to life and seeks revenge."),
    ("The Bamboo Stalk", "Saud Alsanousi", "Novel", 16, "Intermediate",
     "A young man born to a Kuwaiti father and a Filipino mother searches for his identity between two countries and cultures."),
    ("The Granada Trilogy", "Radwa Ashour", "Novel", 16, "Intermediate",
     "Tells the story of the fall of Granada and the forced exile that followed, through the life of one Andalusian family."),
    ("Harry Potter and the Sorcerer's Stone", "J. K. Rowling", "Fantasy", 9, "Beginner",
     "A boy discovers on his eleventh birthday that he is a wizard and joins Hogwarts School of Witchcraft and Wizardry."),
    ("Alice's Adventures in Wonderland", "Lewis Carroll", "Fantasy", 7, "Beginner",
     "A girl follows a white rabbit down a hole and enters a strange world full of odd characters."),
    ("Sophie's World", "Jostein Gaarder", "Philosophy", 15, "Intermediate",
     "A novel that introduces the history of philosophy through mysterious letters sent to a fourteen-year-old girl."),
    ("Atomic Habits", "James Clear", "Self-Help", 15, "Beginner",
     "Explains how small daily changes add up to build good habits and break bad ones."),
    ("The Subtle Art of Not Giving a F*ck", "Mark Manson", "Self-Help", 17, "Intermediate",
     "A frank book that encourages you to choose what is worth caring about instead of trying to care about everything."),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Self-Help", 15, "Beginner",
     "Compares two ways of thinking about money and introduces basic ideas about investing and assets."),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", 18, "Advanced",
     "Describes two modes of human thinking, fast intuitive and slow analytical, and how they shape our decisions."),
    ("A Brief History of Time", "Stephen Hawking", "Science", 16, "Intermediate",
     "Explains the universe from the Big Bang to black holes for readers without a science background."),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "History", 16, "Intermediate",
     "Follows the story of humans from early times to today and how agriculture, religion and money shaped us."),
]
# ---------- Database ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_conn()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            min_age INTEGER NOT NULL,
            level TEXT NOT NULL,
            summary TEXT NOT NULL
        )"""
    )
    count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO books (title, author, genre, min_age, level, summary) VALUES (?,?,?,?,?,?)",
            SEED_BOOKS,
        )
    conn.commit()
    conn.close()


def search_books(text):
    conn = get_conn()
    like = f"%{text}%"
    rows = conn.execute(
        "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?",
        (like, like, like),
    ).fetchall()
    conn.close()
    return rows


def recommend_books(age, level, genres):
    conn = get_conn()
    marks = ",".join("?" * len(genres))
    rows = conn.execute(
        f"SELECT * FROM books WHERE min_age <= ? AND level = ? AND genre IN ({marks})",
        (age, level, *genres),
    ).fetchall()
    conn.close()
    return rows


def all_genres():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT genre FROM books ORDER BY genre").fetchall()
    conn.close()
    return [r["genre"] for r in rows]


def all_books():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return rows


def add_book(title, author, genre, min_age, level, summary):
    conn = get_conn()
    conn.execute(
        "INSERT INTO books (title, author, genre, min_age, level, summary) VALUES (?,?,?,?,?,?)",
        (title, author, genre, min_age, level, summary),
    )
    conn.commit()
    conn.close()


# ---------- Audio ----------
def make_audio(text):
    buf = BytesIO()
    gTTS(text=text, lang="en").write_to_fp(buf)
    buf.seek(0)
    return buf


# ---------- User interface ----------
st.set_page_config(page_title="Book Corner", page_icon="📚", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background-color: #FAF6EE; }
    html, body, [class*="css"] { font-family: 'Georgia', 'Times New Roman', serif; color: #4A3728; }
    h1, h2, h3 { color: #5C3D2E; }
    .line { height: 3px; background: linear-gradient(to right, transparent, #B08968, transparent);
        margin: 8px 0 20px 0; border: none; }
    .card { background: #FFFDF8; border: 1px solid #E3D5BF; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 12px; }
    .card h4 { margin: 0 0 4px 0; color: #5C3D2E; }
    .meta { color: #8B6F5A; font-size: 0.9rem; margin-bottom: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

st.markdown("<h1 style='text-align:center'>📚 Book Corner</h1>", unsafe_allow_html=True)
st.markdown("<hr class='line'>", unsafe_allow_html=True)


def show_book(b):
    st.markdown(
        f"""<div class='card'>
        <h4>{b['title']}</h4>
        <div class='meta'>{b['author']} | {b['genre']} | Level: {b['level']} | Age {b['min_age']}+</div>
        <div>{b['summary']}</div></div>""",
        unsafe_allow_html=True,
    )


tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "✨ Recommend", "🎧 Listen", "➕ Add Book"])

with tab1:
    q = st.text_input("Search by title, author or genre")
    results = search_books(q) if q else all_books()
    st.caption(f"Results: {len(results)}")
    for b in results:
        show_book(b)

with tab2:
    st.write("Tell me about yourself and I will pick suitable books for you.")
    age = st.number_input("Your age", min_value=5, max_value=100, value=18)
    level = st.selectbox("Your reading level", LEVELS)
    genres = st.multiselect("Genres you like", all_genres())
    if st.button("Recommend"):
        if not genres:
            st.warning("Please choose at least one genre.")
        else:
            recs = recommend_books(age, level, genres)
            if recs:
                for b in recs:
                    show_book(b)
            else:
                st.info("No matching books found. Try another level or genre.")

    with tab3:
        books = all_books()
        titles = [b["title"] for b in books]
        choice = st.selectbox("Choose a book to listen to its summary", titles)
        selected = next(b for b in books if b["title"] == choice)
        st.write(selected["summary"])
        if st.button("🔊 Listen"):
            with st.spinner("Preparing audio..."):
                try:
                    st.audio(make_audio(f"{selected['title']}. {selected['summary']}"), format="audio/mp3")
                except Exception as e:
                    st.error(f"Could not prepare audio. Check your internet connection. ({e})")

    with tab4:
        with st.form("add_form", clear_on_submit=True):
            t = st.text_input("Book title")
            a = st.text_input("Author")
            g = st.text_input("Genre (Novel, Science, History...)")
            ma = st.number_input("Minimum suitable age", min_value=5, max_value=100, value=12)
            lv = st.selectbox("Level", LEVELS)
            s = st.text_area("Book summary")
            if st.form_submit_button("Save"):
                if t and a and g and s:
                    add_book(t, a, g, ma, lv, s)
                    st.success("Book added successfully.")
                else:
                    st.error("Please fill in all fields.")
