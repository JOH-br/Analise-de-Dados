
                    CREATE TABLE IF NOT EXISTS buffer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_position TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        turn TEXT NOT NULL,
                        type_position TEXT NOT NULL,
                        category_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        insert_by TEXT NOT NULL,
                        status TEXT NOT NULL);
                    
                    CREATE TABLE IF NOT EXISTS category(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL);

                    CREATE TABLE IF NOT EXISTS buffer_history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        day DATE NOT NULL,
                        quantity INTEGER NOT NULL);
                