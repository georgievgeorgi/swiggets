import asyncio
import csv
import logging
import os.path
import sqlite3
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog
from typing import List

from pydantic import validate_call

from ..core.click_event import MouseButton
from ..core.formatter import Formatter
from ..core.polling import Polling
from ..misc import Icons, timedelta

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self,
                 sqlite_db: str,
                 additional_on_create_sql: List[str] = [],
                 projects: List[str] = [],
                 companies: List[str] = [],
                 activities: List[str] = [],
                 update_interval: int = 300,
                 ):
        self.update_interval = update_interval
        self.sqlite_db = sqlite_db
        self.projects = projects
        self.companies = companies
        self.activities = activities
        additional_on_create_sql
        self.reset()
        self.sqlite_db_setup(additional_on_create_sql=additional_on_create_sql)

    def sqlite_db_setup(self, additional_on_create_sql: List[str] = []):
        if not os.path.exists(self.sqlite_db):
            con = sqlite3.connect(self.sqlite_db)
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute("CREATE TABLE companies("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "name TEXT NOT NULL UNIQUE) STRICT;")
            cur.execute("CREATE TABLE projects("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "name TEXT NOT NULL UNIQUE) STRICT;")
            cur.execute("CREATE TABLE activities("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "name TEXT NOT NULL UNIQUE) STRICT;")
            cur.execute('CREATE TABLE timetrack('
                        'start_time TEXT NOT NULL PRIMARY KEY,'
                        'stop_time TEXT NOT NULL,'
                        'company_id INTEGER NOT NULL,'
                        'project_id INTEGER NOT NULL,'
                        'activity_id INTEGER NOT NULL,'
                        'message TEXT NOT NULL,'
                        'FOREIGN KEY (company_id) REFERENCES companies(id) ON UPDATE RESTRICT ON DELETE RESTRICT,'
                        'FOREIGN KEY (project_id) REFERENCES projects(id) ON UPDATE RESTRICT ON DELETE RESTRICT,'
                        'FOREIGN KEY (activity_id) REFERENCES activities(id) ON UPDATE RESTRICT ON DELETE RESTRICT'
                        ') STRICT;'
                        )
            cur.execute('CREATE VIEW v_timetrack_raw AS SELECT start_time, stop_time,'
                        'c.name AS company, p.name AS project, a.name AS activity,'
                        'ttr.message '
                        'FROM timetrack ttr '
                        'LEFT JOIN companies c ON ttr.company_id = c.id '
                        'LEFT JOIN projects p ON ttr.project_id = p.id '
                        'LEFT JOIN activities a ON ttr.activity_id = a.id '
                        "ORDER BY start_time;"
                        )
            cur.execute("CREATE VIEW v_timetrack_full AS SELECT "
                        "strftime('%Y-%m', ttr.start_time, 'localtime') AS start_month,"
                        "strftime('%Y-%m-%d', ttr.start_time, 'localtime') AS start_date,"
                        "strftime('%u', ttr.start_time, 'localtime') AS start_week_day,"
                        "strftime('%T', ttr.start_time, 'localtime') AS start_hour,"
                        "strftime('%T', ttr.stop_time, 'localtime') AS stop_hour,"
                        "CAST(UNIXEPOCH(ttr.stop_time) - UNIXEPOCH(ttr.start_time) AS REAL)/60/60 AS duration_hours,"
                        "company, project, activity,"
                        "ttr.message "
                        "FROM v_timetrack_raw ttr "
                        "ORDER BY start_time;"
                        )
            cur.execute("CREATE VIEW v_hours_per_month AS SELECT "
                        "start_month, company, project, SUM(duration_hours) "
                        "FROM v_timetrack_full GROUP BY company, project, start_month "
                        "ORDER BY start_date, start_hour;"
                        )
            cur.execute("CREATE VIEW v_daily_load AS SELECT "
                        "start_date, SUM(duration_hours) "
                        "FROM v_timetrack_full GROUP BY start_date "
                        "ORDER BY start_date;"
                        )
            cur.execute("CREATE VIEW v_daily_load_per_project AS SELECT "
                        "start_date, company, project,"
                        "round(SUM(duration_hours), 5) AS duration "
                        "FROM v_timetrack_full GROUP BY start_date, company, project "
                        "ORDER BY strftime('%Y-%m', start_date), company;"
                        )
            for sql in additional_on_create_sql:
                cur.execute(sql)
            con.commit()
            con.close()

    def dump_db(self):
        con = sqlite3.connect(self.sqlite_db)
        cur = con.cursor()
        ret = [i for i in cur.execute('SELECT * FROM v_timetrack_raw;')]
        con.commit()
        con.close()
        return ret

    def insert_replace_db(self, start_time, stop_time, company, project, activity, message):
        con = sqlite3.connect(self.sqlite_db)
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("INSERT OR REPLACE INTO companies (name) "
                    "SELECT ? WHERE NOT EXISTS "
                    "(SELECT 1 FROM companies WHERE name = ?);",
                    (company, company))
        cur.execute("INSERT INTO projects (name) "
                    "SELECT ? WHERE NOT EXISTS "
                    "(SELECT 1 FROM projects WHERE name = ?);",
                    (project, project))
        cur.execute("INSERT INTO activities (name) "
                    "SELECT ? WHERE NOT EXISTS "
                    "(SELECT 1 FROM activities WHERE name = ?);",
                    (activity, activity))
        cur.execute(
            "INSERT OR REPLACE INTO timetrack("
            "start_time, stop_time, company_id, project_id, activity_id, message) "
            "VALUES("
            "(SELECT strftime('%FT%TZ', ?, 'utc')),"
            "(SELECT strftime('%FT%TZ', ?, 'utc')),"
            "(SELECT id FROM companies WHERE name LIKE(?)),"
            "(SELECT id FROM projects WHERE name LIKE(?)),"
            "(SELECT id FROM activities WHERE name LIKE(?)),"
            "?);", (
                start_time,
                stop_time,
                company,
                project,
                activity,
                message,
                ))
        con.commit()
        con.close()

    def reset(self):
        self.is_running = False
        self.start_time = None
        self.stop_time = None
        self.message = ''
        self.project = ''
        self.company = ''
        self.activity = ''
        self.ok_clicked = False

    def add_update_record_db(self):
        self.insert_replace_db(
            start_time=time.strftime('%FT%TZ', time.gmtime(self.start_time)),
            stop_time=time.strftime('%FT%TZ', time.gmtime(self.stop_time)),
            company=self.company,
            project=self.project,
            activity=self.activity,
            message=self.message,
        )

    async def toggle(self):
        if self.is_running:
            await self.stop()
        else:
            await self.start()

    async def start(self):
        self.start_time = time.time()
        self.stop_time = time.time() + self.update_interval/2
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.gui)
            while future.running():
                await asyncio.sleep(.1)
        if self.ok_clicked:
            self.is_running = True
            self.ok_clicked = False
            self.add_update_record_db()

    async def stop(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.gui)
            while future.running():
                await asyncio.sleep(.1)
        if self.ok_clicked:
            self.stop_time = time.time()
            self.add_update_record_db()
            self.reset()
            self.ok_clicked = False

    async def update(self):
        # update stop time every few minutes
        # prevent data loss in case of crash
        if self.is_running:
            if time.time() > self.stop_time + self.update_interval/2:
                self.add_update_record_db()

    async def import_csv(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: filedialog.askopenfile(
                title='Import timetrack from csv',
                filetypes=[('csv', '*.csv')],
                initialdir=os.path.dirname(self.sqlite_db),
            ))
            while future.running():
                await asyncio.sleep(.1)
            fd = future.result()
            if fd is not None:
                dat = csv.reader(fd)
                for line in dat:
                    self.insert_replace_db(*line)

    async def export_csv(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(lambda: filedialog.asksaveasfile(
                title='Export timetrack to csv',
                filetypes=[('csv', '*.csv')],
                defaultextension='.csv',
                initialdir=os.path.dirname(self.sqlite_db),
                initialfile=f"{time.strftime(
                    '%FT%TZ', time.gmtime())}-{os.path.basename(self.sqlite_db)}.csv",
            ))
            while future.running():
                await asyncio.sleep(.1)
            fd = future.result()
            if fd is not None:
                wrt = csv.writer(fd, quoting=csv.QUOTE_MINIMAL)
                wrt.writerows(self.dump_db())

    @property
    def elapsed(self):
        dt = timedelta(seconds=int(time.time() - self.start_time))
        return dt

    def gui(self):
        root = tk.Tk()
        selected_project = tk.StringVar(root)
        selected_company = tk.StringVar(root)
        selected_activity = tk.StringVar(root)
        selected_message = tk.StringVar(root)

        selected_project.set(self.project)
        selected_company.set(self.company)
        selected_activity.set(self.activity)
        selected_message.set(self.message)

        def ok_button_disabler(*args):
            if len(selected_project.get()) and len(selected_company.get()) and \
               len(selected_activity.get()) and len(selected_message.get()):
                ok_btn.config(state='normal')
            else:
                ok_btn.config(state='disabled')

        selected_project.trace_add(['write', 'unset'], ok_button_disabler)
        selected_company.trace_add(['write', 'unset'], ok_button_disabler)
        selected_activity.trace_add(['write', 'unset'], ok_button_disabler)
        selected_message.trace_add(['write', 'unset'], ok_button_disabler)

        def ok():
            self.project = selected_project.get()
            self.activity = selected_activity.get()
            self.company = selected_company.get()
            self.message = selected_message.get()
            self.ok_clicked = True
            root.destroy()

        root.title('Time Tracker')
        root.geometry('500x300')
        root.wm_attributes('-type', 'splash')
        root.bind('<Escape>', root.destroy)
        proj_frame = tk.LabelFrame(root, text='Project')

        comp_frame = tk.LabelFrame(root, text='Company')
        for comp in self.companies:
            tk.Radiobutton(comp_frame, text=comp, value=comp,
                           variable=selected_company).pack(anchor='w')
        comp_frame.grid(column=0, row=0, padx=5, pady=5, ipadx=10, ipady=10, sticky=tk.NE+tk.SW)

        for prj in self.projects:
            tk.Radiobutton(proj_frame, text=prj, value=prj,
                           variable=selected_project).pack(anchor='w')
        proj_frame.grid(column=1, row=0, padx=5, pady=5,
                        ipadx=10, ipady=10, sticky=tk.NE+tk.SW)

        act_frame = tk.LabelFrame(root, text='Activity')
        for act in self.activities:
            tk.Radiobutton(act_frame, text=act, value=act,
                           variable=selected_activity).pack(anchor='w')
        act_frame.grid(column=2, row=0, padx=5, pady=5,
                       ipadx=10, ipady=10, sticky=tk.NE+tk.SW)

        tk.Entry(root, textvariable=selected_message).grid(
            column=0, row=1, columnspan=3, padx=5, pady=5,
            ipadx=10, ipady=10, sticky=tk.NE+tk.SW)

        btn_frame = tk.Frame(root)
        btn_frame.grid(column=0, row=2, columnspan=3, padx=5, pady=5,
                       ipadx=10, ipady=10, sticky=tk.NE+tk.SW)
        ok_btn = tk.Button(btn_frame, text='OK', command=ok)
        ok_btn.pack(side='left', expand=True)
        ok_button_disabler()
        tk.Button(btn_frame, text='Cancel', command=root.destroy).pack(
            side='left', expand=True)

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.mainloop()


class TimeTrack(Polling):
    @validate_call(config=dict(validate_default=True))
    def __init__(self,
                 sqlite_db: str,
                 additional_on_create_sql: List[str] = [],
                 interval=60,
                 update_interval=300,
                 format_full: Formatter = (
                     Icons.stopwatch + ' {company}:{project} ({activity}) {elapsed:%h:%M} : {message:0.10}'
                     ),
                 format_short: Formatter = Icons.stopwatch + ' {company}:{project} ({activity})',
                 format_stopped: str = Icons.stopwatch,
                 projects: list[str] = ['proj1', 'proj2'],
                 companies: list[str] = ['comp1', 'comp2'],
                 activities: list[str] = ['General', 'Software', 'Hardware',
                                          'Documentation', 'Discussion',
                                          'Research',
                                          'Administrative'],
                 **kwargs):
        super().__init__(interval=min(interval, update_interval/2), **kwargs)
        self.task_mngr = TaskManager(additional_on_create_sql=additional_on_create_sql,
                                     sqlite_db=sqlite_db,
                                     projects=projects,
                                     activities=activities,
                                     companies=companies,
                                     update_interval=update_interval)
        self.block = self.add_block(name=type(self).__name__)

        self.format_full = format_full
        self.format_short = format_short
        self.format_stopped = format_stopped
        self.update_text()
        self.update()

    def update_text(self):
        if self.task_mngr.is_running:
            dat = dict(
                company=self.task_mngr.company,
                activity=self.task_mngr.activity,
                project=self.task_mngr.project,
                message=self.task_mngr.message,
                elapsed=self.task_mngr.elapsed,
            )
            self.block.full_text = self.format_full(**dat)
            self.block.short_text = self.format_short(**dat)
        else:
            self.block.full_text = self.format_stopped
            self.block.short_text = self.format_stopped

    async def loop(self):
        await self.task_mngr.update()
        self.update_text()
        self.update()

    async def click_event(self, evt):
        if evt.button == MouseButton.left:
            await self.task_mngr.toggle()
            self.block.urgent = self.task_mngr.is_running
            self.update_text()
        elif evt.button == MouseButton.right:
            await self.task_mngr.import_csv()
        elif evt.button == MouseButton.middle:
            await self.task_mngr.export_csv()
        self.update()
