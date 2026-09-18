#  Advanced Blog Application (Module 10)

This is an enhanced continuation of the Module 9 Django Blog Application, extending the architecture with **Django Model Relationships, Advanced ORM Aggregations & Annotations, Query Optimization (`select_related`, `prefetch_related`), Nested Comments, Likes, and 1-5 Star Ratings**.

---

## 🎯 Key Enhancements & Implemented Features

### 1. Comment & Nested Reply System
- **Self-referential Relationship**: Implemented `parent = models.ForeignKey('self', ...)` to allow multi-level, nested replies (Rahim -> Karim -> Rahim).
- **CRUD & Authorization**: Authenticated users can create, read, edit, and delete their own comments. Unauthorized edits/deletions raise `PermissionDenied` (HTTP 403).

### 2.  Like / Unlike System
- **Post Likes & Comment Likes**: Implemented `PostLike` and `CommentLike` models with `unique_together` constraints to prevent duplicate likes from the same user.
- Dynamically displays total likes for posts and comments.

### 3.  1–5 Star Rating System
- `PostRating` model with `MinValueValidator(1)` and `MaxValueValidator(5)`.
- Users can submit and update their ratings. Duplicate ratings are prevented using `unique_together = ('post', 'user')` and `update_or_create`.
- Displays real-time average rating (`Avg('ratings__rating')`) and total rating count.

### 4.  Aggregations, Annotations & Engagement
- Uses Django ORM's `Count()` and `Avg()` to calculate total likes, total comments, and average ratings directly in the SQL layer.
- **Popular Posts**: Uses annotation and ordering (`order_by('-total_likes', '-avg_rating')`) instead of Python loop logic.

### 5. Search & Filtering
- Search across post title (`title__icontains`), content (`content__icontains`), and author username (`author__username__icontains`).
- Optional filter by minimum rating (`avg_rating__gte`).

### 6.  Query Optimization (`select_related` & `prefetch_related`)
- **`select_related('author')`**: Uses SQL `INNER JOIN` to fetch the post and comment authors in a single query, eliminating $N+1$ query overhead.
- **`prefetch_related('likes', 'replies__author', ...)`**: Performs optimized batch queries across reverse foreign keys and nested relationships.

### 7. User Profile Statistics
- Displays personalized metrics: Total posts, total comments, likes given, and ratings given.

### 8.  Django Admin Customization
- Admin interface lists total comments, likes count, and formatted average ratings using custom annotated QuerySets.

---

##  Tech Stack

- **Backend**: Python, Django (>=4.2)
- **Database**: SQLite3
- **Frontend**: Django Templates, Bootstrap 5, Bootstrap Icons

---

##  Local Setup Instructions

```bash
# 1. Virtual environment setup
python -m venv env
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create admin account (Optional)
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/`

---


