
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

from repositories.db import migrate
from repositories.endpoint_repository import EndpointRepository
from repositories.check_result_repository import CheckResultRepository
from models.endpoint import Endpoint
from probe.http_checker import HttpChecker
from analysis.llm_analyzer import LLMAnalyzer

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "app.db"


class NetGuardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NetGuard Network Error Detection Dashboard")
        self.root.geometry("1400x850")

        migrate()

        self.endpoint_repo = EndpointRepository()
        self.result_repo = CheckResultRepository()
        self.checker = HttpChecker()
        self.analyzer = LLMAnalyzer()

        title = tk.Label(
            root,
            text="NetGuard Network Error Detection Dashboard",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Prototype interface for monitoring endpoints, running checks, and viewing LLM-assisted results",
            font=("Arial", 11)
        )
        subtitle.pack(pady=5)

        summary_frame = tk.Frame(root)
        summary_frame.pack(pady=10)

        self.endpoints_label = tk.Label(summary_frame, text="Endpoints: 0", font=("Arial", 11, "bold"))
        self.endpoints_label.grid(row=0, column=0, padx=20)

        self.checks_label = tk.Label(summary_frame, text="Total Checks: 0", font=("Arial", 11, "bold"))
        self.checks_label.grid(row=0, column=1, padx=20)

        self.ok_label = tk.Label(summary_frame, text="OK Results: 0", font=("Arial", 11, "bold"))
        self.ok_label.grid(row=0, column=2, padx=20)

        self.error_label = tk.Label(summary_frame, text="Errors: 0", font=("Arial", 11, "bold"))
        self.error_label.grid(row=0, column=3, padx=20)

        add_frame = tk.LabelFrame(root, text="Add Endpoint", font=("Arial", 11, "bold"))
        add_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(add_frame, text="Name:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = tk.Entry(add_frame, width=30, font=("Arial", 10))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_frame, text="URL:", font=("Arial", 10)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.url_entry = tk.Entry(add_frame, width=50, font=("Arial", 10))
        self.url_entry.grid(row=0, column=3, padx=10, pady=10)

        add_button = tk.Button(
            add_frame,
            text="Add Endpoint",
            font=("Arial", 10, "bold"),
            command=self.add_endpoint
        )
        add_button.grid(row=0, column=4, padx=15, pady=10)

        content_frame = tk.Frame(root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = tk.LabelFrame(content_frame, text="Endpoints", font=("Arial", 11, "bold"))
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        right_frame = tk.LabelFrame(content_frame, text="Check Results", font=("Arial", 11, "bold"))
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.endpoint_tree = ttk.Treeview(
            left_frame,
            columns=("id", "name", "url", "enabled", "expected_latency"),
            show="headings",
            height=18
        )
        self.endpoint_tree.pack(fill="both", expand=True)

        self.endpoint_tree.heading("id", text="ID")
        self.endpoint_tree.heading("name", text="Name")
        self.endpoint_tree.heading("url", text="URL")
        self.endpoint_tree.heading("enabled", text="Enabled")
        self.endpoint_tree.heading("expected_latency", text="Expected Latency")

        self.endpoint_tree.column("id", width=50)
        self.endpoint_tree.column("name", width=140)
        self.endpoint_tree.column("url", width=300)
        self.endpoint_tree.column("enabled", width=80)
        self.endpoint_tree.column("expected_latency", width=140)

        self.result_tree = ttk.Treeview(
            right_frame,
            columns=("id", "endpoint_id", "ts", "latency", "status", "http_status", "llm_label"),
            show="headings",
            height=18
        )
        self.result_tree.pack(fill="both", expand=True)

        self.result_tree.heading("id", text="ID")
        self.result_tree.heading("endpoint_id", text="Endpoint ID")
        self.result_tree.heading("ts", text="Timestamp")
        self.result_tree.heading("latency", text="Latency (ms)")
        self.result_tree.heading("status", text="Status")
        self.result_tree.heading("http_status", text="HTTP Code")
        self.result_tree.heading("llm_label", text="LLM Label")

        self.result_tree.column("id", width=50)
        self.result_tree.column("endpoint_id", width=90)
        self.result_tree.column("ts", width=180)
        self.result_tree.column("latency", width=95)
        self.result_tree.column("status", width=80)
        self.result_tree.column("http_status", width=90)
        self.result_tree.column("llm_label", width=120)

        llm_frame = tk.LabelFrame(root, text="Latest LLM Analysis", font=("Arial", 11, "bold"))
        llm_frame.pack(fill="x", padx=10, pady=10)

        self.llm_text = tk.Text(llm_frame, height=5, wrap="word", font=("Arial", 10))
        self.llm_text.pack(fill="x", padx=10, pady=10)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        check_button = tk.Button(
            button_frame,
            text="Check Selected Endpoint",
            font=("Arial", 11, "bold"),
            command=self.run_check_selected
        )
        check_button.grid(row=0, column=0, padx=10)

        delete_button = tk.Button(
            button_frame,
            text="Delete Selected Endpoint",
            font=("Arial", 11, "bold"),
            command=self.delete_selected_endpoint
        )
        delete_button.grid(row=0, column=1, padx=10)

        clear_button = tk.Button(
            button_frame,
            text="Clear All Data",
            font=("Arial", 11, "bold"),
            command=self.clear_all_data
        )
        clear_button.grid(row=0, column=2, padx=10)

        export_button = tk.Button(
            button_frame,
            text="Export Results to Excel",
            font=("Arial", 11, "bold"),
            command=self.export_to_excel
        )
        export_button.grid(row=0, column=3, padx=10)

        self.load_data()

    def get_conn(self):
        return sqlite3.connect(DB_PATH)

    def add_endpoint(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()

        if not name or not url:
            messagebox.showerror("Input Error", "Please enter both a name and a URL.")
            return

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            self.endpoint_repo.add(Endpoint(
                id=None,
                name=name,
                url=url
            ))

            self.name_entry.delete(0, tk.END)
            self.url_entry.delete(0, tk.END)

            self.load_data()
            messagebox.showinfo("Success", f"Endpoint '{name}' added successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add endpoint:\n{e}")

    def run_check_selected(self):
        selected = self.endpoint_tree.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select an endpoint first.")
            return

        item = self.endpoint_tree.item(selected[0])
        endpoint_id = item["values"][0]
        endpoint_name = item["values"][1]
        endpoint_url = item["values"][2]
        endpoint_enabled = bool(item["values"][3])
        expected_latency = item["values"][4]

        endpoint = Endpoint(
            id=endpoint_id,
            name=endpoint_name,
            url=endpoint_url,
            enabled=endpoint_enabled,
            expected_latency_ms=expected_latency
        )

        result = self.checker.check(endpoint)
        raw_label, final_label, final_explanation = self.analyzer.analyze_result(endpoint.name, result)

        result.llm_label = final_label
        result.llm_analysis = final_explanation

        self.result_repo.add(result)
        self.load_data()

        messagebox.showinfo("Check Complete", f"Finished checking '{endpoint.name}'.")

    def delete_selected_endpoint(self):
        selected = self.endpoint_tree.selection()

        if not selected:
            messagebox.showwarning("No Selection", "Please select an endpoint to delete.")
            return

        item = self.endpoint_tree.item(selected[0])
        endpoint_id = item["values"][0]
        endpoint_name = item["values"][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete endpoint '{endpoint_name}' and all of its check results?"
        )

        if confirm:
            self.endpoint_repo.delete(endpoint_id)
            self.load_data()

    def clear_all_data(self):
        confirm = messagebox.askyesno(
            "Confirm Clear",
            "This will delete ALL endpoints and ALL check results. Continue?"
        )

        if confirm:
            self.endpoint_repo.clear_all()
            self.load_data()

    def export_to_excel(self):
        try:
            conn = self.get_conn()

            query = """
            SELECT
                cr.id AS Check_ID,
                e.name AS Endpoint_Name,
                e.url AS Endpoint_URL,
                cr.ts AS Timestamp,
                cr.latency_ms AS Latency_ms,
                cr.status AS Status,
                cr.http_status AS HTTP_Code,
                cr.error_type AS Error_Type,
                cr.error_message AS Error_Message,
                cr.llm_label AS LLM_Label,
                cr.llm_analysis AS LLM_Analysis
            FROM check_results cr
            JOIN endpoints e ON cr.endpoint_id = e.id
            ORDER BY cr.id DESC
            """

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                messagebox.showwarning("No Data", "There are no check results to export.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel Report",
                initialfile="netguard_check_results.xlsx"
            )

            if not file_path:
                return

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Check Results")

                worksheet = writer.sheets["Check Results"]

                for column_cells in worksheet.columns:
                    max_length = 0
                    column_letter = column_cells[0].column_letter
                    for cell in column_cells:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    worksheet.column_dimensions[column_letter].width = max_length + 2

            messagebox.showinfo("Export Complete", f"Excel file saved successfully:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel file:\n{e}")

    def load_data(self):
        for item in self.endpoint_tree.get_children():
            self.endpoint_tree.delete(item)

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        conn = self.get_conn()

        endpoints = conn.execute(
            "SELECT id, name, url, enabled, expected_latency_ms FROM endpoints"
        ).fetchall()

        results = conn.execute(
            """
            SELECT id, endpoint_id, ts, latency_ms, status, http_status, llm_label, llm_analysis
            FROM check_results
            ORDER BY id DESC
            """
        ).fetchall()

        conn.close()

        for row in endpoints:
            self.endpoint_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

        for row in results:
            self.result_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        total_endpoints = len(endpoints)
        total_checks = len(results)
        ok_results = len([r for r in results if r[4] == "OK"])
        error_results = len([r for r in results if r[4] == "ERROR"])

        self.endpoints_label.config(text=f"Endpoints: {total_endpoints}")
        self.checks_label.config(text=f"Total Checks: {total_checks}")
        self.ok_label.config(text=f"OK Results: {ok_results}")
        self.error_label.config(text=f"Errors: {error_results}")

        self.llm_text.delete("1.0", tk.END)
        if results:
            latest_analysis = results[0][7]
            if latest_analysis:
                self.llm_text.insert(tk.END, latest_analysis)
            else:
                self.llm_text.insert(tk.END, "No LLM analysis available yet.")
        else:
            self.llm_text.insert(tk.END, "No check results available yet.")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetGuardGUI(root)
    root.mainloop()
