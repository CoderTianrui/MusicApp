# API Documentation

This project implements a series of RESTful APIs designed for user authentication, playlist management, music handling, and session control. Each API endpoint is designed to handle specific tasks, and this document provides a detailed description of each endpoint, including the HTTP method, request parameters, and responses.

## Base URL
All APIs are accessed via the following base URL:
```
https://your-domain.com/api/
```

## Authentication
Some API endpoints require the user to be authenticated. Authentication is handled using session cookies. CSRF protection is enabled on most endpoints unless stated otherwise.

---

### 1. `/login/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Logs in the user using email and password, with multi-factor authentication (MFA). Returns session and CSRF tokens.  

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "yourpassword",
  "mfa_code": "123456"
}
```

**Response**:
```json
{
  "message": "Logged in successfully",
  "session_token": "session_token_value",
  "csrftoken": "csrf_token_value"
}
```

**Error Response**:
- 400 Bad Request: Invalid credentials or MFA code.
- 429 Too Many Requests: Rate-limiting after multiple failed attempts.

---

### 2. `/logout/`
**Method**: `POST`  
**Input**: None  
**Output**: `JSON`  
**CSRF Exempted**: Yes  
**Description**: Logs out the current user and invalidates the session.  

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

**Error Response**:
- 400 Bad Request: Invalid session.

---

### 3. `/session/`
**Method**: `POST`  
**Input**: None  
**Output**: `JSON`  
**CSRF Exempted**: Yes  
**Description**: Retrieves session information and returns the authenticated user details if the session is valid.

**Response**:
```json
{
  "user": "user@example.com",
  "role": 1
}
```

**Error Response**:
- 401 Unauthorized: Session not found or user not authenticated.

---

### 4. `/get_csrf_token/`
**Method**: `GET`  
**Input**: None  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Returns a new CSRF token for secure form submissions.

**Response**:
```json
{
  "csrf_token": "csrf_token_value"
}
```

---

### 5. `/register/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Registers a new user and generates an MFA secret. Returns a QR code for MFA setup.  

**Request Body**:
```json
{
  "username": "user@example.com",
  "password": "yourpassword",
  "name": "John Doe",
  "displayname": "Johnny"
}
```

**Response**:
```json
{
  "message": "User registered successfully",
  "qr_code": "data:image/png;base64,..."
}
```

**Error Response**:
- 400 Bad Request: Invalid input or user already exists.

---

### 6. `/create_playlist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Creates a new playlist for the authenticated user.

**Request Body**:
```json
{
  "title": "My Playlist"
}
```

**Response**:
```json
{
  "message": "Playlist created successfully",
  "playlist_id": 123,
  "title": "My Playlist",
  "owner": "user@example.com"
}
```

**Error Response**:
- 400 Bad Request: Playlist already exists.
- 401 Unauthorized: User not authenticated.

---

### 7. `/add_track_to_playlist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Adds a track to an existing playlist.

**Request Body**:
```json
{
  "playlist_id": 123,
  "track_id": 456
}
```

**Response**:
```json
{
  "message": "Track added to playlist",
  "playlist_id": 123,
  "track_id": 456
}
```

**Error Response**:
- 400 Bad Request: Playlist or track not found.
- 401 Unauthorized: User not authenticated.

---

### 8. `/share_playlist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Shares a playlist with another user.

**Request Body**:
```json
{
  "playlist_id": 123,
  "user_id": 789
}
```

**Response**:
```json
{
  "message": "Playlist shared successfully",
  "playlist_id": 123,
  "user_id": 789
}
```

**Error Response**:
- 400 Bad Request: Playlist or user not found.
- 401 Unauthorized: User not authenticated.

---

### 9. `/get_album/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Exempted**: Yes  
**Description**: Retrieves information about a specific album.

**Request Body**:
```json
{
  "album_name": "Album Title"
}
```

**Response**:
```json
{
  "message": "Album found",
  "album_data": {
    "title": "Album Title",
    "release_date": "2024-10-25",
    "label": "Music Label",
    "description": "Description of the album"
  }
}
```

**Error Response**:
- 404 Not Found: Album not found.

---

### 10. `/get_music/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: Audio File (FLAC)  
**CSRF Exempted**: Yes  
**Description**: Streams the requested music file to the client.

**Request Body**:
```json
{
  "music_name": "track.flac"
}
```

**Response**: Returns the audio file stream.

**Error Response**:
- 404 Not Found: Music file not found.

---

### 11. `/add_track/`
**Method**: `POST` (multipart form data)  
**Input**: `Multipart Form`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Adds a new track to the system.

**Request Body** (multipart form data):
- `title` (string)
- `duration` (string)
- `releaseDate` (date)
- `file` (audio file)
- `lyrics` (optional)

**Response**:
```json
{
  "message": "Track added successfully",
  "track_id": 456
}
```

**Error Response**:
- 400 Bad Request: Missing or invalid fields.
- 403 Forbidden: User does not have permission.

---

### 12. `/add_album/`
**Method**: `POST` (multipart form data)  
**Input**: `Multipart Form`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Adds a new album to the system.

**Request Body** (multipart form data):
- `title` (string)
- `totalTracks` (integer)
- `label` (string)
- `releaseDate` (date)
- `file` (image file)
- `description` (string)

**Response**:
```json
{
  "message": "Album added successfully",
  "album_id": 123
}
```

**Error Response**:
- 400 Bad Request: Missing or invalid fields.
- 403 Forbidden: User does not have permission.

---

### 13. `/add_artist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Adds a new artist to the system.

**Request Body**:
```json
{
  "name": "Artist Name",
  "debutDate": "2024-01-01",
  "bio": "Artist biography"
}
```

**Response**:
```json
{
  "message": "Artist added successfully",
  "artist_id": 789
}
```

**Error Response**:
- 400 Bad Request: Missing or invalid fields.
- 403 Forbidden: User does not have permission.

---

### 14. `/add_genre/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Adds a new genre to the system.

**Request Body**:
```json
{
  "name": "Genre Name",
  "description": "Genre description"
}
```

**Response**:
```json
{
  "message": "Genre added successfully",
  "genre_id": 101
}
```

**Error Response**:
- 400 Bad Request: Missing or invalid fields.
- 403 Forbidden: User does not have permission.

---

### 15. `/link_track_to_album/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Links a track to an album.

**Request Body**:
```json
{
  "trackName": "Track Title",
  "albumName": "Album Title"
}
```

**Response**:
```json
{
  "message": "Track linked to album successfully"
}
```

**Error Response**:
- 400 Bad Request: Track or album not found.
- 403 Forbidden: User does not have permission.

---

### 16. `/link_album_to_artist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Links an album to an artist.

**Request Body**:
```json
{
  "albumName": "Album Title",
  "artistName": "Artist Name"
}
```

**Response**:
```json
{
  "message": "Album linked to artist successfully"
}
```

**Error Response**:
- 400 Bad Request: Album or artist not found.
- 403 Forbidden: User does not have permission.

---

### 17. `/link_track_to_artist/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Links a track to an artist.

**Request Body**:
```json
{
  "trackName": "Track Title",
  "artistName": "Artist Name"
}
```

**Response**:
```json
{
  "message": "Track linked to artist successfully"
}
```

**Error Response**:
- 400 Bad Request: Track or artist not found.
- 403 Forbidden: User does not have permission.

---

### 18. `/link_track_to_genre/`
**Method**: `POST`  
**Input**: `JSON`  
**Output**: `JSON`  
**CSRF Protected**: Yes  
**Description**: Links a track to a genre.

**Request Body**:
```json
{
  "trackName": "Track Title",
  "genreName": "Genre Name"
}
```

**Response**:
```json
{
  "message": "Track linked to genre successfully"
}
```

**Error Response**:
- 400 Bad Request: Track or genre not found.
- 403 Forbidden: User does not have permission.

---

### 19. `/search_songs/`
**Method**: `GET`  
**Input**: Query Parameter (`query`)  
**Output**: `JSON` (List of Songs)  
**CSRF Exempted**: Yes  
**Description**: Searches for songs by title.

**Request**: `/search_songs/?query=songtitle`

**Response**:
```json
[
  {
    "trackNumber": 1,
    "title": "Song Title",
    "duration": "3:45",
    "url": "song.flac"
  }
]
```

**Error Response**:
- 200 OK: Empty array if no results are found.

---

### 20. `/search_albums/`
**Method**: `GET`  
**Input**: Query Parameter (`query`)  
**Output**: `JSON` (List of Albums)  
**CSRF Exempted**: Yes  
**Description**: Searches for albums by title.

**Request**: `/search_albums/?query=albumtitle`

**Response**:
```json
[
  {
    "albumNumber": 1,
    "title": "Album Title",
    "release_date": "2024-10-25",
    "label": "Music Label",
    "description": "Album description"
  }
]
```

**Error Response**:
- 200 OK: Empty array if no results are found.

---

### Error Codes
Common error codes used across the API:
- `400`: Bad Request (Invalid input data).
- `401`: Unauthorized (Authentication required or invalid).
- `403`: Forbidden (Permission denied).
- `404`: Not Found (Resource not found).
- `429`: Too Many Requests (Rate limiting).
- `500`: Internal Server Error (Unhandled exception).

---

## Notes
- **Authentication**: Most APIs require a valid session and session cookies. Make sure to include the `sessionid` and `csrftoken` in requests that require authentication and CSRF protection.
- **Permissions**: Some endpoints (like adding albums or tracks) require admin-level permissions.
- **File Upload**: Endpoints that handle file uploads (like `/add_track/` and `/add_album/`) expect multipart form data.
