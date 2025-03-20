import mysql.connector

import pytest

@pytest.fixture(scope="function")
def pripojeni_db():
    
    conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="****",
            database="ukoly"
    )

    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS ukoly_test (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nazev VARCHAR(100) NOT NULL,
                    popis VARCHAR(255) NOT NULL,
                    stav VARCHAR(25) NOT NULL,
                    DatumVytvoreni DATE 
                );
            ''')
    

    conn.commit()

    yield conn, cursor

    cursor.execute("DROP TABLE IF EXISTS ukoly_test ;")
    conn.commit()

    cursor.close()
    conn.close()

  

def test_pridat_ukol(pripojeni_db):
        conn,cursor = pripojeni_db
        cursor = conn.cursor()

        cursor.execute("INSERT INTO ukoly_test (nazev,popis,stav) VALUES ('nazev pro úkol','popis pro úkol', 'Nezahájeno');")
        cursor.execute("SELECT * FROM ukoly_test WHERE nazev = 'nazev pro úkol';")
        result = cursor.fetchone()
        assert result is not None, "Úkol nebyl přidán"

def test_pridat_prazdny_ukol(pripojeni_db):
        conn, cursor = pripojeni_db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly_test (nazev,popis,stav) VALUES ('nazev pro úkol','   ', 'Nezahájeno');")
        cursor.execute("SELECT * FROM ukoly_test WHERE nazev IS NULL OR popis IS NULL;")
        result = cursor.fetchone()
        assert result is  None, "Úkol byl úspěšně přidán" 

def test_aktualizovat_ukol(pripojeni_db):
        conn, cursor = pripojeni_db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly_test (nazev,popis,stav) VALUES ('nazev pro úkol','poips pro úkol ', 'Nezahájeno');")
        
        cursor.execute("UPDATE ukoly_test SET stav = 'Probihá';")
        
        cursor.execute("SELECT * FROM ukoly_test WHERE stav = 'Probihá'; ")
        result = cursor.fetchone()
        assert result is not None, "Úkol nebyl úspěšně aktualizovan" 

def test_aktualizovat_ukol_z_neplatnym_id(pripojeni_db):
        conn, cursor = pripojeni_db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly_test (nazev,popis,stav) VALUES ('nazev pro úkol','poips pro úkol ', 'Nezahájeno');")
        cursor.execute("UPDATE ukoly_test SET stav = 'Hotovo' WHERE id = 10;")
        cursor.execute("SELECT * FROM ukoly_test WHERE id = 10; ")

        result = cursor.fetchone()
        assert result is  None, "Úkol byl úspěšně aktualizovan"


def test_odstranit_ukol(pripojeni_db):
        conn, cursor = pripojeni_db
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ukoly_test (nazev,popis,stav) VALUES ('nazev pro úkol','poips pro úkol ', 'Nezahájeno');")
       
        cursor.execute("DELETE FROM ukoly_test WHERE id = 1;")
        conn.commit()
      
        cursor.execute("SELECT * FROM ukoly_test WHERE id = 1;")
        result = cursor.fetchone()
        assert result is  None, "Záznam nebyl správně smazán."


def test_odstranit_ukol_z_neplatnym_id(pripojeni_db):   
     conn, cursor = pripojeni_db
     cursor = conn.cursor()


     cursor.execute("SELECT COUNT(*) FROM ukoly_test;")
     initial_count = cursor.fetchone()[0]

 # Mazání neexistujícího záznamu
     cursor.execute("DELETE FROM ukoly_test WHERE id = 15;")
     conn.commit()

    # Počet záznamů po testu
     cursor.execute("SELECT COUNT(*) FROM ukoly_test;")
     final_count = cursor.fetchone()[0]

    # Ověření, že počet záznamů zůstal stejný
     assert initial_count == final_count, "Mazání neexistujícího záznamu změnilo stav databáze."




