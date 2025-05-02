from werkzeug.security import generate_password_hash
from app import db, Item, app  # Ensure `app` is imported
from datetime import datetime, timedelta
import random
from app import User, Rental


def random_last_issued_date():
    if random.choice([True, False]):  # Randomly decide if the item was issued
        return random_date(2024, 2025)  # Random date between 2022 and 2025
    return None

def random_date(start_year, end_year):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def populate_items():
    with app.app_context():  # Add application context
        # Clear existing items
        Item.query.delete()

        # Predefined lists of titles with their genres
        video_cd_genres = {
            "The Lord of the Rings: The Return of the King": "Fantasy",
            "Star Wars: A New Hope": "Sci-Fi",
            "Star Wars: The Empire Strikes Back": "Sci-Fi",
            "Star Wars: Return of the Jedi": "Sci-Fi",
            "Jurassic Park": "Adventure",
            "Titanic": "Romance",
            "Avatar": "Sci-Fi",
            "Avengers: Endgame": "Action",
            "Black Panther": "Action",
            "Spider-Man: No Way Home": "Action",
            "The Lion King": "Animation",
            "Toy Story": "Animation"
        }

        music_cd_genres = {
            "Thriller - Michael Jackson": "Pop",
            "Back in Black - AC/DC": "Rock",
            "The Dark Side of the Moon - Pink Floyd": "Progressive Rock",
            "The Wall - Pink Floyd": "Progressive Rock",
            "Abbey Road - The Beatles": "Rock",
            "Sgt. Pepper's Lonely Hearts Club Band - The Beatles": "Rock",
            "Rumours - Fleetwood Mac": "Rock",
            "Hotel California - Eagles": "Rock",
            "Born to Run - Bruce Springsteen": "Rock",
            "Purple Rain - Prince": "Pop",
            "1989 - Taylor Swift": "Pop",
            "25 - Adele": "Pop",
            "Lemonade - Beyoncé": "R&B",
            "Nevermind - Nirvana": "Grunge",
            "Appetite for Destruction - Guns N' Roses": "Hard Rock",
            "Led Zeppelin IV - Led Zeppelin": "Hard Rock",
            "A Night at the Opera - Queen": "Rock",
            "American Idiot - Green Day": "Punk Rock",
            "The Marshall Mathers LP - Eminem": "Hip-Hop",
            "Fearless - Taylor Swift": "Country",
            "Born This Way - Lady Gaga": "Pop",
            "Random Access Memories - Daft Punk": "Electronic",
            "Future Nostalgia - Dua Lipa": "Pop",
            "Divide - Ed Sheeran": "Pop",
            "Folklore - Taylor Swift": "Indie Folk"
        }

        dvd_genres = {
            "Harry Potter and the Sorcerer's Stone": "Fantasy",
            "Harry Potter and the Chamber of Secrets": "Fantasy",
            "Harry Potter and the Prisoner of Azkaban": "Fantasy",
            "Harry Potter and the Goblet of Fire": "Fantasy",
            "Harry Potter and the Order of the Phoenix": "Fantasy",
            "Harry Potter and the Half-Blood Prince": "Fantasy",
            "Harry Potter and the Deathly Hallows: Part 1": "Fantasy",
            "Harry Potter and the Deathly Hallows: Part 2": "Fantasy",
            "Shrek": "Animation",
            "Frozen": "Animation",
            "Moana": "Animation",
            "Coco": "Animation",
            "Finding Nemo": "Animation",
            "Inside Out": "Animation",
            "Up": "Animation",
            "WALL-E": "Animation",
            "Monsters, Inc.": "Animation",
            "The Incredibles": "Animation",
            "Ratatouille": "Animation",
            "Brave": "Animation",
            "Tangled": "Animation",
            "Zootopia": "Animation",
            "Despicable Me": "Animation",
            "Minions": "Animation",
            "How to Train Your Dragon": "Animation"
        }

        vhs_genres = {
            "E.T. the Extra-Terrestrial": "Sci-Fi",
            "The Wizard of Oz": "Fantasy",
            "Casablanca": "Romance",
            "Gone with the Wind": "Romance",
            "Jaws": "Thriller",
            "Rocky": "Drama",
            "The Sound of Music": "Musical",
            "Grease": "Musical",
            "Back to the Future": "Sci-Fi",
            "Indiana Jones and the Raiders of the Lost Ark": "Adventure",
            "Indiana Jones and the Temple of Doom": "Adventure",
            "Indiana Jones and the Last Crusade": "Adventure",
            "The Breakfast Club": "Drama",
            "Ferris Bueller's Day Off": "Comedy",
            "Dirty Dancing": "Romance",
            "Ghostbusters": "Comedy",
            "Top Gun": "Action",
            "The Goonies": "Adventure",
            "Stand by Me": "Drama",
            "The Princess Bride": "Fantasy",
            "Labyrinth": "Fantasy",
            "The NeverEnding Story": "Fantasy",
            "Who Framed Roger Rabbit": "Animation",
            "Beetlejuice": "Comedy",
            "The Little Mermaid": "Animation"
        }

        # Combine all titles into a single list with their types and genres
        all_items = [
                        (title, "video_cd", genre) for title, genre in video_cd_genres.items()
                    ] + [
                        (title, "music_cd", genre) for title, genre in music_cd_genres.items()
                    ] + [
                        (title, "dvd", genre) for title, genre in dvd_genres.items()
                    ] + [
                        (title, "vhs", genre) for title, genre in vhs_genres.items()
                    ]

        # Add items to the database
        for title, genre in music_cd_genres.items():
            item = Item(
                title=title,
                type="music_cd",
                genre=genre,
                daily_rate=round(random.uniform(5, 25), 2),
                purchase_price=round(random.uniform(100, 300), 2),
                available=True,
                date_added = random_date(2023, 2025),
                last_issued_date = random_last_issued_date()
            )
            db.session.add(item)

        for title, genre in video_cd_genres.items():
            item = Item(
                title=title,
                type="video_cd",
                genre=genre,
                daily_rate=round(random.uniform(30, 100), 2),
                purchase_price=round(random.uniform(500, 650), 2),
                available=True,
                date_added = random_date(2023, 2025),
                last_issued_date = random_last_issued_date()

            )
            db.session.add(item)

        for title, genre in dvd_genres.items():
            item = Item(
                title=title,
                type="dvd",
                genre=genre,
                daily_rate=round(random.uniform(100, 250), 2),
                purchase_price=round(random.uniform(600, 800), 2),
                available=True,
                date_added = random_date(2023, 2025),
                last_issued_date = random_last_issued_date()
            )
            db.session.add(item)

        for title, genre in vhs_genres.items():
            item = Item(
                title=title,
                type="vhs",
                genre=genre,
                daily_rate=round(random.uniform(10, 50), 2),
                purchase_price=round(random.uniform(400, 500), 2),
                available=True,
                date_added = random_date(2023, 2025),
                last_issued_date = random_last_issued_date()
            )
            db.session.add(item)

        # Commit changes
        db.session.commit()
        print("Items populated successfully!")


if __name__ == "__main__":
    populate_items()