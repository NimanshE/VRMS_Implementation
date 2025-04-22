# populate_db.py
from werkzeug.security import generate_password_hash

from app import db, Item, app  # Ensure `app` is imported
from datetime import datetime, timedelta
import random
from app import User, Rental

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
                available=True,
                date_added=datetime.utcnow()
            )
            db.session.add(item)

        for title, genre in video_cd_genres.items():
            item = Item(
                title=title,
                type="video_cd",
                genre=genre,
                daily_rate=round(random.uniform(30, 100), 2),
                available=True,
                date_added=datetime.utcnow()
            )
            db.session.add(item)

        for title, genre in dvd_genres.items():
            item = Item(
                title=title,
                type="dvd",
                genre=genre,
                daily_rate=round(random.uniform(100, 250), 2),
                available=True,
                date_added=datetime.utcnow()
            )
            db.session.add(item)

        for title, genre in vhs_genres.items():
            item = Item(
                title=title,
                type="vhs",
                genre=genre,
                daily_rate=round(random.uniform(10, 50), 2),
                available=True,
                date_added=datetime.utcnow()
            )
            db.session.add(item)

        # Commit changes
        db.session.commit()
        print("Items populated successfully!")


def populate_users():
    with app.app_context():
        # Clear existing users
        User.query.delete()

        # Predefined users
        users = [
            {"name": "Admin User", "email": "admin@example.com", "password": "admin123", "role": "admin"},
            {"name": "Clerk User", "email": "clerk@example.com", "password": "clerk123", "role": "clerk"},
            {"name": "John Doe", "email": "john.doe@example.com", "password": "password123", "role": "customer", "deposit": 1500.00},
            {"name": "Jane Smith", "email": "jane.smith@example.com", "password": "password123", "role": "customer", "deposit": 2000.00},
            {"name": "Alice Johnson", "email": "alice.johnson@example.com", "password": "password123", "role": "customer", "deposit": 1000.00},
        ]

        for user_data in users:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password=generate_password_hash(user_data["password"]),
                role=user_data["role"],
                deposit=user_data.get("deposit", 0.00),
                membership_active=user_data["role"] == "customer",
                date_joined=datetime.utcnow()
            )
            db.session.add(user)

        db.session.commit()
        print("Users populated successfully!")

def populate_rentals():
    with app.app_context():
        # Clear existing rentals
        Rental.query.delete()

        # Fetch users and items
        customers = User.query.filter_by(role="customer").all()
        items = Item.query.all()

        # Generate random rentals
        for _ in range(20):  # Create 20 random rentals
            customer = random.choice(customers)
            item = random.choice(items)
            rental_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            due_date = rental_date + timedelta(days=random.randint(1, 14))
            return_date = rental_date + timedelta(days=random.randint(1, 14)) if random.random() > 0.5 else None
            status = "returned" if return_date else "approved"

            rental = Rental(
                user_id=customer.id,
                item_id=item.id,
                rental_date=rental_date,
                due_date=due_date,
                return_date=return_date,
                status=status,
                total_charge=round(item.daily_rate * (return_date - rental_date).days if return_date else item.daily_rate * (due_date - rental_date).days, 2)
            )
            db.session.add(rental)

        db.session.commit()
        print("Rentals populated successfully!")

if __name__ == "__main__":
    populate_items()
    populate_users()
    populate_rentals()