import sqlite3
import jdatetime as jd


class DBService:

    def __init__(self, db_path: str):
        self.db_path = db_path
        #self.date = jd.datetime.now().strftime("%Y-%m-%d")
    

    def _get_conn(self):
        return sqlite3.connect(self.db_path) 


    def get_equip_detail(self, equip_code):
        conn = self._get_conn()
        cursor = conn.cursor()

        # 1) equipment info
        cursor.execute("""
            SELECT equipment_id, name, pm_type, location, notes
            FROM equipment
            WHERE equipment_code = ?
        """, (equip_code,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            return None  # or raise

        equipment_id, name, pm_type, location, notes = row
        # print(equipment_id, name, pm_type, location, notes)

        data = {
            "equip_code": equip_code,
            "equip_id": equipment_id,
            "name": name,
            "equip_type": pm_type,
            "location": location,
            "note": notes,
            "pm": []   
        }

        cursor.execute("""
            SELECT pm_name,
                duration_days,
                COALESCE(last_done_date, ''),
                COALESCE(next_due_date, ''),
                is_active
            FROM equipment_pm_task
            WHERE equipment_id = ?
            ORDER BY pm_name
        """, (equipment_id,))
        rows = cursor.fetchall()
        conn.close()

        for pm_name, duration_days, last_done, next_due, is_active in rows:
            pm_entry = [
                pm_name,
                duration_days,
                last_done,
                next_due,
                bool(is_active)
            ]
            data["pm"].append(pm_entry)

        return data       

    def load_equipment_table(self):
        #NOTE: can query and get equip_note too! show in main_page
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT equipment_code, location, pm_type
            FROM equipment
            ORDER BY equipment_code
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows


    def mark_a_pm_done(self, equipment_code, pm_name, last_done_date):
        """
        Mark a PM task as done for an equipment.
        Computes next_due_date = last_done_date + duration_days.
        
        Args:
            equipment_code: int (e.g. 1001)
            pm_name: str (e.g. 'check shaft')
            last_done_date: str (Jalali date like '1404-10-11')
        
        Returns: equipment_pm_id of the updated task
        """
        conn = self._get_conn()
        cur = conn.cursor()
        
        # 1) Find equipment_id from equipment_code
        cur.execute("""
            SELECT equipment_id 
            FROM equipment 
            WHERE equipment_code = ?
        """, (equipment_code,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"equipment_code {equipment_code} not found")
        equipment_id = row[0]
        
        # 2) Find the PM task and get its duration_days
        cur.execute("""
            SELECT equipment_pm_id, duration_days 
            FROM equipment_pm_task 
            WHERE equipment_id = ? AND pm_name = ? AND is_active = 1
        """, (equipment_id, pm_name))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"PM task '{pm_name}' not found for equipment {equipment_code}")
        equipment_pm_id, duration_days = row
        
        # 3) Compute next_due_date (you'll replace this with real Jalali math)
        # TODO: use jdatetime or similar: next_due_date = jalali_date(last_done_date) + duration_days


        jdate_obj = jd.datetime.strptime(last_done_date,  '%Y-%m-%d')
        next_date = jdate_obj+jd.timedelta(days=duration_days)
        next_due_date = next_date.strftime('%Y-%m-%d')
        
        # 4) Update the task
        cur.execute("""
            UPDATE equipment_pm_task 
            SET last_done_date = ?, 
                next_due_date = ?
            WHERE equipment_pm_id = ?
        """, (last_done_date, next_due_date, equipment_pm_id))
        
        conn.commit()
        conn.close()
    
        print(f"Marked PM '{pm_name}' done for equipment {equipment_code}")
        print(f"  equipment_pm_id: {equipment_pm_id}")
        print(f"  last_done: {last_done_date}, next_due: {next_due_date}")
    
        return equipment_pm_id


    def delete_equipment(self, equipment_code):
        # DIDN'T TEST YET!
        conn = self._get_conn()
        cur = conn.cursor()
        # 1) Find equipment_id first
        cur.execute("""
            SELECT equipment_id 
            FROM equipment 
            WHERE equipment_code = ?
        """, (equipment_code,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"equipment_code {equipment_code} not found")
        equipment_id = row[0]
        
        # 2) Delete pm_work_order records first (if you have this table)
        cur.execute("""
            DELETE FROM equipment_pm_task 
            WHERE equipment_pm_id IN (
                SELECT equipment_pm_id FROM equipment_pm_task WHERE equipment_id = ?
            )
        """, (equipment_id,))
        
        # 3) Delete equipment_pm_task records
        cur.execute("""
            DELETE FROM equipment_pm_task 
            WHERE equipment_id = ?
        """, (equipment_id,))
        
        # 4) Delete equipment itself
        cur.execute("""
            DELETE FROM equipment 
            WHERE equipment_id = ?
        """, (equipment_id,))
        
        conn.commit()
        conn.close() 
        print(f"Deleted equipment {equipment_code} (id={equipment_id})")
        print(f"  - Deleted {cur.rowcount} equipment_pm_task records")
        print(f"  - Deleted {cur.rowcount} equipment record")
        
        return equipment_id


    def add_new_equipment(self, equipment_code, pm_type, location):
        # can add name, note param later
        conn = self._get_conn()
        cursor = conn.cursor()
        command = f"""
        INSERT INTO equipment (
            equipment_code,
            name,
            pm_type,
            location,
            notes
        ) VALUES (?, ?, ?, ?, ?)
        """
        values = (equipment_code, "NOTHING", pm_type, location, "NOTE:")
        try:
            cursor.execute(command, values)
            conn.commit()
            conn.close()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            conn.close()
            return "Duplicated"
        return 1


    def add_pm_tasks_for_equipment(self, equipment_code):
        conn = self._get_conn()
        cur = conn.cursor()

        # 1) find equipment_id and pm_type from equipment_code
        cur.execute("""
            SELECT equipment_id, pm_type
            FROM equipment
            WHERE equipment_code = ?
        """, (equipment_code,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"equipment_code {equipment_code} not found")
        equipment_id, pm_type = row

        # 2) find template_id for this pm_type (A, B, ...)
        cur.execute("""
            SELECT template_id
            FROM pm_template
            WHERE template_code = ?
        """, (pm_type,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"PM template '{pm_type}' not found")
        template_id = row[0]

        # 3) get all template tasks for that template
        cur.execute("""
            SELECT template_task_id, pm_name, duration_days
            FROM pm_template_task
            WHERE template_id = ?
        """, (template_id,))
        tasks = cur.fetchall()
        if not tasks:
            raise ValueError(f"No tasks defined for template '{pm_type}' (id={template_id})")

        # 4) insert tasks into equipment_pm_task WITHOUT dates
        for template_task_id, pm_name, duration_days in tasks:
            cur.execute("""
                INSERT INTO equipment_pm_task (
                    equipment_id,
                    template_task_id,
                    pm_name,
                    duration_days,
                    last_done_date,
                    next_due_date
                ) VALUES (?, ?, ?, ?, NULL, NULL)
            """, (
                equipment_id,
                template_task_id,
                pm_name,
                duration_days
            ))

        conn.commit()
        conn.close()    

    #create_sarlak_failures_report()
    def insert_failure(self, device, tarikh, start_time="", stop_reason="", duration=0, description=""):
        """
        اضافه کردن رکورد خرابی جدید به دیتابیس
        
        پارامترها:
        device (str): نام دستگاه
        tarikh (str): تاریخ فارسی
        start_time (str): زمان شروع (مثل "14:30")
        stop_reason (str): علت توقف
        duration (int): مدت زمان به دقیقه
        description (str): توضیحات
        """
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO failures 
                (device, tarikh, start_time, stop_reason, duration, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device, tarikh, start_time, stop_reason, duration, description))
            
            conn.commit()
            failure_id = cursor.lastrowid
            print(f"{failure_id} اضافه شد")
            
            return failure_id
            
        except Exception as e:
            print(f"ERROR: {e}")
            return None
            
        finally:
            conn.close()

    def get_all_failures_sl_ORIGIN(self):
        """
        [(ID, device, tarikh, start_time, stop_reason, duration, description), ...]
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, device, tarikh, start_time, stop_reason, duration, description
                FROM failures
                ORDER BY tarikh DESC, start_time DESC
            """)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"ERROR in get_all_failures: {e}")
            return []
        finally:
            conn.close()

    def get_all_failures_sl(self, from_date=None, to_date=None):
        """
        [(ID, device, tarikh, start_time, stop_reason, duration, description), ...]
        """

        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, device, tarikh, start_time, stop_reason, duration, description
                FROM failures
            """

            params = []

            if from_date and to_date:
                query += " WHERE tarikh BETWEEN ? AND ? "
                params.extend([
                    from_date.strftime("%Y-%m-%d"),
                    to_date.strftime("%Y-%m-%d")
                ])

            query += " ORDER BY tarikh DESC, start_time DESC "

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows

        except Exception as e:
            print(f"ERROR in get_all_failures: {e}")
            return []
        finally:
            conn.close()


    def delete_failure(self, failure_id: int) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM failures WHERE id = ?", (failure_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"ERROR in delete_failure: {e}")
            return False
        finally:
            conn.close()







        


db_file = "/home/ahoora/work/CMMS/god.db"



def create_sarlak_stat():
    conn = sqlite3.connect(db_file)
    pass

def create_sarlak_failures_report():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT NOT NULL,
                stop_reason TEXT,
                start_time TEXT,
                duration INTEGER,
                description TEXT,
                tarikh TEXT NOT NULL
            )
        ''')
    conn.commit()


# insert_failure("PU1", "1404-10-23", "15:49", "خرابی سینی", 120, "به دلیل فلان بهمان")
def insert_into_pm_template(template_type):
    """just add pm_template LIKE Type A / Type B"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    command = f"""
    INSERT INTO pm_template (template_code)
    VALUES ('{template_type}')
    """ 

    cursor.execute(command)
    conn.commit()
    conn.close()
    print("DONE")
    
# insert_into_pm_template("DESMA")
#insert_into_pm_template("PU2")

def insert_pm_template_type_x_task():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    command = f"""
    INSERT INTO pm_template_task (template_id, pm_name, duration_days)
    VALUES
    (5, 'DESMA_task1', 1),
    (5, 'DESMA_task2', 7),
    (5, 'DESMA_task3', 7),
    (5, 'DESMA_task4', 7),
    (5, 'DESMA_task6', 10),
    (5, 'DESMA_task7', 10),
    (5, 'DESMA_task8', 10),
    (5, 'DESMA_task9', 30),
    (5, 'DESMA_task10', 30),
    (5, 'DESMA_task11', 30),
    (5, 'DESMA_task12', 365),
    (5, 'DESMA_task13', 365),
    (5, 'DESMA_task14', 365),
    (5, 'DESMA_task15', 365);
    """ 
    # (1, ...): [1] is come from (SELECT template_id FROM pm_template WHERE template_code = 'A';) or check in sqlite3browser

    cursor.execute(command)
    conn.commit()
    conn.close()

#insert_pm_template_type_x_task()





# now = jd.datetime.now().strftime("%Y-%m-%d")
# mark_a_pm_done(1001, "A1", now)




# data = get_equip_detail(1001)
# print(data['pm'])