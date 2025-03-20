import mysql.connector
import datetime
import pytest



def pripojeni_db():
    
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Fed91+5:A",
            database="ukoly"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Chyba při připojování: {e}")
        return None
        
def vytvoreni_tabulky(connection,test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
   
    cursor = connection.cursor()
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            ( id INT AUTO_INCREMENT PRIMARY KEY,
                    nazev VARCHAR(100) NOT NULL,
                    popis VARCHAR(255) NOT NULL,
                    stav VARCHAR(25) NOT NULL,
                    DatumVytvoreni DATE  );       
                   
                 """ )
    except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}")  

    connection.commit()
    cursor.close()


    
def pridat_ukol(connection, nazev, popis,test_mode=False ):
    
    table_name = "ukoly_test" if test_mode else "ukoly"
    datum_vytvoreni = datetime.date.today()
    cursor = connection.cursor()
    if not nazev.strip() or not popis.strip():
       print("Zadal prázdný vstup. Zkus to znovu!")
    else:
        try:
           cursor.execute(f"INSERT INTO {table_name} (nazev, popis, stav, DatumVytvoreni) VALUES (%s, %s,'Nezahájeno',%s)", (nazev, popis,datum_vytvoreni,)) 
           connection.commit()
           print(f"Úkol {nazev} přdán do tabulky {table_name }.")
        except mysql.connector.Error as e:
            print(f"Chyba: {e}")
        
    cursor.close()
    
def zobrazit_ukoly(connection, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {table_name} ")
    for rows in cursor.fetchall():
        print(rows) 
    if cursor.rowcount == 0:
        print(f"Seznam úkolů je prázdný.")
               
    connection.commit()
    cursor.close()

def filtr_stavu(connection, test_mode=False): 
    table_name = "ukoly_test" if test_mode else "ukoly" 
        
    cursor = connection.cursor()     
    try: 
        stav = input("Zadej stav úkoly'Nezahájeno' nebo 'Probihá': ")
        cursor.execute( f"SELECT * FROM {table_name} WHERE stav = %s ", ( stav,))
        for rows in cursor.fetchall():
            print(rows)
        if cursor.rowcount == 0:       
            print("Úkolů z takym svavom neni" )
               
        connection.commit()
            
    except mysql.connector.Error as err:
        print(f"Chyba pří čteni dat: {err}")  
        connection.commit()      
    cursor.close()

def aktualizovat_ukol(connection,id,stav, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    
    cursor = connection.cursor(dictionary=True)   
      
    update_ukoly = (f" UPDATE {table_name} SET stav = %s WHERE id = %s")
    cursor.execute(update_ukoly, (stav, id))
    connection.commit()
    
    if cursor.rowcount > 0:
        print(f"Záznam z ID:{id} byl aktualizován")
    else:
        print(f"Úkol s ID {id} nebyl nalezen.Neplatné číslo úkolu. Zkuste to znovu.")
        
    cursor.close()
            

def odstranit_ukol(connection, id, test_mode=False):
    table_name = "ukoly_test" if test_mode else "ukoly"
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (id,))
    print("Odstraneno úkol:", cursor.rowcount) 
    connection.commit()

    if cursor.rowcount > 0:
        print(f"Úkol s ID {id} byl smazán.")
    else:
        print(f"Úkol s ID {id} nebyl nalezen.Neplatné číslo úkolu. Zkuste to znovu.")
        
    cursor.close()
    connection.close()

@pytest.fixture(scope ="module")
def connection():
    connection = pripojeni_db()
    vytvoreni_tabulky(connection, test_mode=True)
    yield connection

    cursor = connection.cursor()
    try: 
        cursor.execute(f"DROP TABLE IF EXISTS ukoly_test")
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Chyba při mazání testovací tabulky: {e}")
    cursor.close()
    connection.close()
   

def test_pridat_ukol(connection):
   
    pridat_ukol(connection, "test ukol","test popis", test_mode=True)
    ukol = zobrazit_ukoly(connection, test_mode=True) 
    assert ukol is None, "Úkol  nebyl přidán"



def test_pridat_ukol_bez_nazvu(connection):
    
    ukol = pridat_ukol(connection, "  ","test popis", test_mode=True)  
    print("\n Pokus o načtení neexistujíciho úkola:")
    print(f" Výsledek: {ukol}")
    assert ukol is  None,"Záznam byl vložen do tabulky."
   

def test_aktualizovat_ukol(connection):      
    ukol = aktualizovat_ukol(connection, 1, "Hotovo",  test_mode=True)
    
    
    print("\n Pokus o aktualizacii úkola:")
    print(f" Výsledek: {ukol}")
    assert ukol is  None, "Záznam nebyl aktualizovan"


def test_aktualizovat_ukol_z_neplatnym_id(connection):
    ukol = aktualizovat_ukol(connection, 9999 ,"Hotovo", test_mode=True)

    print("\n Pokus o aktualizacii úkola:")
    print(f" Výsledek: {ukol}")
    assert ukol is None, "Záznam byl aktualizovan"

def test_odstranit_ukol(connection):
    pridat_ukol(connection, "test ukol","test popis", test_mode=True)
    ukol = odstranit_ukol(connection, 1,  test_mode=True)
    print(f" Výsledek: {ukol}")
    assert ukol is None, "Záznam byl odstranen"

def test_mazani_neexistujiciho_zaznamu(connection):
    
    ukol = odstranit_ukol(connection, 999, test_mode=True)
    print(f" Výsledek: {ukol}")
    assert ukol is None, "Záznam byl odstranen"






TESTS ={
"1": " test_pridat_ukol",
"2": " test_pridat_ukol_bez_nazvu",
"3": " test_aktualizovat_ukol",
"4": " test_aktualizovat_ukol_z_neplatnym_id",
"5": " test_odstranit_ukol",
"6": " test_mazani_neexistujiciho_zaznamu",
"7": " Spustit všechny testy"
} 

if __name__ =="__main__":
    connection = pripojeni_db()
    vytvoreni_tabulky(connection)
        
    

while True:
       print("\nSprávce úkolů - Hlavní menu")
       print("1. Přidat  úkol") 
       print("2. Zobrazit úkoly")
       print("3. Aktualizovat úkol")
       print("4. Odstranit úkol")
       print("5. Spustit testy")
       print("6. Konec programu")
        
       volba = input("Vyberte možnost (1 - 6):")
        
       if volba == "1":
            nazev = input("Zadejte název úkolu: ")
            popis = input("Zadejte popis úkolu: ")
           
            pridat_ukol(connection, nazev, popis)
                
       elif volba == "2":
            zobrazit_ukoly(connection, test_mode=False)
            filtr =input(f"Chcete vyfiltrovat podle stavu? Ano nebo NE: ")
            if filtr == "Ano":
                filtr_stavu(connection,  test_mode=False)
            else:
                None    
           

       elif volba == "3":
           zobrazit_ukoly(connection, test_mode=False)
           id = input("Zadejte číslo úkolu, který chcete aktualizovat: ")
           stav = input("Zadej stav úkoly,který chcete aktualizovat: 'Hotovo' nebo 'Probiha': ")
           
           aktualizovat_ukol(connection, id, stav, test_mode=False)
               
          
       elif volba == "4":
            zobrazit_ukoly(connection, test_mode=False)
            id = input("Zadejte číslo úkolu, který chcete odstranit: ").strip()
            id_int = int(id)
            odstranit_ukol(connection,id, test_mode=False)

       elif volba == "5":
            print("\n Možnosti testů:")
            for key, value in TESTS.items():
                print(f"{key}{value}")
            test_volba = input("Vyber test k provedení:")
            if test_volba in TESTS:
                if test_volba == "7":
                    pytest.main(["-s", "-v", __file__])
                else:    
                    pytest.main(["-s","-v", __file__ , "-k", TESTS[test_volba]])
                print("\n Test dokončen.Stiskni Enter pro návrat do menu")
                input()

       elif volba == "6":
           print("Konec programu")
           connection.close()
           break
       else:
           print("Neplatná volba. Zkuste to znovu.")