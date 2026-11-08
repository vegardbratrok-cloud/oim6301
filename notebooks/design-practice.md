# TV Show Database ERD

```mermaid
erDiagram
    SHOWS ||--o{ ACTORS : "has"
    SHOWS ||--o{ WRITER : "has"
    SHOWS ||--o{ VOTES : "has"

    SHOWS {
        int Show_ID PK
        string Type
        string Genre
        string Rating
        int Year
    }

    ACTORS {
        int Actor_ID PK
        string First_Name
        string Last_Name
        int Show_ID FK
        date DOB
    }

    WRITER {
        int Writer_ID PK
        string First_Name
        string Last_Name
        int Show_ID FK
        date DOB
    }

    VOTES {
        int Vote_ID PK
        int Show_ID FK
        int Score "1-10"
        date Date
    }
```
