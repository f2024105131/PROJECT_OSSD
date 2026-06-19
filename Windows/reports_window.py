"""
TeddyShine Laundry Management System - Reports Window Module
Color Theme: Light Greenish-Gray (#E8F0E6 background style)
Module: reports_window.py
Purpose: View summary reports and analytics (Admin only)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database import get_connection, close_connection
from auth import is_admin, get_current_user
from helpers import (
    show_error, show_success, center_window,
    format_date, format_currency, safe_float, safe_int
)


class ReportsWindow(tk.Frame):
    """
    Reports Window - View summary reports and analytics (Admin only).
    Provides tabs for Monthly Summary, Order Payments Trace, Staff Workload, and Print Receipt Log.
    """
    
    # Modern color theme
    COLORS = {
        'bg': '#E8F0E6',           # Light greenish-gray background
        'card_bg': '#FFFFFF',       # White for cards
        'primary': '#2E7D32',       # Dark green
        'primary_dark': '#1B5E20',  # Darker green for hover
        'primary_light': '#4CAF50', # Light green
        'accent': '#81C784',        # Soft green accent
        'text': '#1B5E20',          # Dark green text
        'text_secondary': '#555555', # Secondary text
        'text_light': '#FFFFFF',    # Light text for buttons
        'border': '#C8E6C9',        # Light green border
        'danger': '#F44336',        # Danger red
        'warning': '#FF9800',       # Warning orange
        'success': '#4CAF50',       # Success green
        'info': '#2196F3',          # Info blue
        'header_bg': '#F5F9F4',     # Light header background
        'access_denied_bg': '#FFEBEE', # Light red for access denied
        'alternate_row': '#F9F9F9'  # Light gray for alternate rows
    }
    
    def __init__(self, parent, go_back_callback):
        """
        Initialize the Reports Window.
        
        Args:
            parent: The parent window (tk.Tk or tk.Frame)
            go_back_callback: Function to call when back button is clicked
        """
        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_columnconfigure(0, weight=1)
        
        # Create UI sections
        self.create_header()
        
        # Check admin access
        if is_admin():
            self.create_main_content()
            self.load_all_reports()
        else:
            self.create_access_denied()
            
    def create_header(self):
        """Creates the header bar with title and back button."""
        header_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        # Configure columns
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
        
        # Back button
        back_btn = tk.Button(
            header_frame,
            text="← Back to Dashboard",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary_dark'],
            fg=self.COLORS['text_light'],
            activebackground=self.COLORS['primary'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8,
            command=self.go_back_callback
        )
        back_btn.grid(row=0, column=0, padx=20, pady=15, sticky='w')
        
        # Hover effect
        def on_enter(e):
            back_btn.config(bg=self.COLORS['primary'])
            
        def on_leave(e):
            back_btn.config(bg=self.COLORS['primary_dark'])
            
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        # Title with admin badge
        title_frame = tk.Frame(header_frame, bg=self.COLORS['primary'])
        title_frame.grid(row=0, column=1, padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="Reports & Analytics",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.pack(side='left')
        
        # Admin badge
        admin_badge = tk.Label(
            title_frame,
            text="🔒 Admin Only",
            font=('Helvetica', 9, 'bold'),
            bg=self.COLORS['warning'],
            fg='white',
            padx=8,
            pady=2
        )
        admin_badge.pack(side='left', padx=(10, 0))
        
        # Last updated label
        self.last_updated_label = tk.Label(
            header_frame,
            text="Last Updated: --",
            font=('Helvetica', 10),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.last_updated_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_access_denied(self):
        """Creates the access denied screen for non-admin users."""
        main_frame = tk.Frame(self, bg=self.COLORS['access_denied_bg'])
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Access denied card
        card = tk.Frame(
            main_frame,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['danger'],
            highlightthickness=2
        )
        card.grid(row=0, column=0, padx=50, pady=50)
        
        # Lock icon
        lock_label = tk.Label(
            card,
            text="🔒",
            font=('Segoe UI Emoji', 64),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['danger']
        )
        lock_label.pack(pady=(30, 10))
        
        # Title
        title_label = tk.Label(
            card,
            text="Access Denied",
            font=('Helvetica', 24, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['danger']
        )
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = tk.Label(
            card,
            text="This section is restricted to administrators only.\n\n"
                 "Reports and analytics are available exclusively for admin users.\n\n"
                 "Please contact your system administrator for access.",
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary'],
            justify='center'
        )
        message_label.pack(pady=(0, 30))
        
        # Go back button
        back_btn = tk.Button(
            card,
            text="← Return to Dashboard",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.go_back_callback
        )
        back_btn.pack(pady=(0, 30))
        
    def create_main_content(self):
        """Creates the main content area with notebook tabs."""
        main_container = tk.Frame(self, bg=self.COLORS['bg'])
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create Notebook (Tabbed interface)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Configure style for notebook
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11))
        
        # Tab 1: Monthly Summary
        self.monthly_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.monthly_frame, text="📊 Monthly Summary")
        self.create_monthly_tab()
        
        # Tab 2: Order Payments Trace
        self.order_payments_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.order_payments_frame, text="💰 Order Payments Trace")
        self.create_order_payments_tab()
        
        # Tab 3: Staff Workload
        self.staff_workload_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.staff_workload_frame, text="👥 Staff Workload")
        self.create_staff_workload_tab()
        
        # Tab 4: Print Receipt Log
        self.print_log_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.print_log_frame, text="🖨️ Print Receipt Log")
        self.create_print_log_tab()
        
    # ==============================================
    # TAB 1: MONTHLY SUMMARY
    # ==============================================
    
    def create_monthly_tab(self):
        """Creates the Monthly Summary report tab."""
        # Control frame
        control_frame = tk.Frame(self.monthly_frame, bg=self.COLORS['bg'])
        control_frame.pack(fill='x', pady=(0, 15))
        
        # Year selection
        tk.Label(
            control_frame,
            text="Year:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(0, 10))
        
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(
            control_frame,
            textvariable=self.year_var,
            values=[str(y) for y in range(2024, datetime.now().year + 2)],
            state='readonly',
            width=8
        )
        self.year_combo.pack(side='left', padx=(0, 15))
        self.year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_monthly_summary())
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_monthly_summary
        )
        refresh_btn.pack(side='right')
        
        # Treeview frame
        tree_frame = tk.Frame(self.monthly_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('Month', 'Total Invoices', 'Paid Invoices', 'Unpaid Invoices', 
                   'Partial Invoices', 'Total Collected', 'Remaining')
        self.monthly_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Define headings
        self.monthly_tree.heading('Month', text='Month')
        self.monthly_tree.heading('Total Invoices', text='Total Invoices')
        self.monthly_tree.heading('Paid Invoices', text='Paid Invoices')
        self.monthly_tree.heading('Unpaid Invoices', text='Unpaid Invoices')
        self.monthly_tree.heading('Partial Invoices', text='Partial Invoices')
        self.monthly_tree.heading('Total Collected', text='Total Collected')
        self.monthly_tree.heading('Remaining', text='Remaining')
        
        # Define column widths
        self.monthly_tree.column('Month', width=120, anchor='center')
        self.monthly_tree.column('Total Invoices', width=120, anchor='center')
        self.monthly_tree.column('Paid Invoices', width=120, anchor='center')
        self.monthly_tree.column('Unpaid Invoices', width=120, anchor='center')
        self.monthly_tree.column('Partial Invoices', width=120, anchor='center')
        self.monthly_tree.column('Total Collected', width=150, anchor='center')
        self.monthly_tree.column('Remaining', width=150, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.monthly_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.monthly_tree.xview)
        self.monthly_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.monthly_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
    def load_monthly_summary(self):
        """Loads monthly summary data."""
        # Clear existing items
        for item in self.monthly_tree.get_children():
            self.monthly_tree.delete(item)
            
        year = self.year_var.get()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Monthly summary query
            query = """
                SELECT 
                    strftime('%Y-%m', i.generated_date) as month,
                    strftime('%m', i.generated_date) as month_num,
                    strftime('%Y', i.generated_date) as year,
                    CASE strftime('%m', i.generated_date)
                        WHEN '01' THEN 'January'
                        WHEN '02' THEN 'February'
                        WHEN '03' THEN 'March'
                        WHEN '04' THEN 'April'
                        WHEN '05' THEN 'May'
                        WHEN '06' THEN 'June'
                        WHEN '07' THEN 'July'
                        WHEN '08' THEN 'August'
                        WHEN '09' THEN 'September'
                        WHEN '10' THEN 'October'
                        WHEN '11' THEN 'November'
                        WHEN '12' THEN 'December'
                    END as month_name,
                    COUNT(i.invoice_id) as total_invoices,
                    SUM(CASE WHEN i.status = 'Paid' THEN 1 ELSE 0 END) as paid_invoices,
                    SUM(CASE WHEN i.status = 'Unpaid' THEN 1 ELSE 0 END) as unpaid_invoices,
                    SUM(CASE WHEN i.status = 'Partial' THEN 1 ELSE 0 END) as partial_invoices,
                    COALESCE(SUM(i.amount_paid), 0) as total_collected,
                    COALESCE(SUM(i.balance_due), 0) as remaining
                FROM Invoice i
                WHERE strftime('%Y', i.generated_date) = ?
                GROUP BY month
                ORDER BY month_num ASC
            """
            
            cursor.execute(query, (year,))
            rows = cursor.fetchall()
            
            total_collected_overall = 0
            total_remaining_overall = 0
            
            for row in rows:
                self.monthly_tree.insert('', 'end', values=(
                    row['month_name'],
                    row['total_invoices'],
                    row['paid_invoices'],
                    row['unpaid_invoices'],
                    row['partial_invoices'],
                    format_currency(row['total_collected']),
                    format_currency(row['remaining'])
                ))
                total_collected_overall += row['total_collected']
                total_remaining_overall += row['remaining']
            
            # Add totals row if there are records
            if rows:
                self.monthly_tree.insert('', 'end', values=(
                    '━━━ TOTAL ━━━',
                    '━━━',
                    '━━━',
                    '━━━',
                    '━━━',
                    format_currency(total_collected_overall),
                    format_currency(total_remaining_overall)
                ), tags=('total',))
                
                # Configure total row style
                self.monthly_tree.tag_configure('total', background=self.COLORS['header_bg'], font=('Helvetica', 10, 'bold'))
                
            self.update_last_updated()
            
        except Exception as e:
            print(f"[ReportsWindow] Error loading monthly summary: {e}")
            show_error(f"Failed to load monthly summary: {str(e)}")
        finally:
            close_connection(conn)
            
    # ==============================================
    # TAB 2: ORDER PAYMENTS TRACE
    # ==============================================
    
    def create_order_payments_tab(self):
        """Creates the Order Payments Trace report tab."""
        # Control frame
        control_frame = tk.Frame(self.order_payments_frame, bg=self.COLORS['bg'])
        control_frame.pack(fill='x', pady=(0, 15))
        
        # Status filter
        tk.Label(
            control_frame,
            text="Order Status:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(0, 10))
        
        self.order_status_filter = ttk.Combobox(
            control_frame,
            values=['All', 'Pending', 'Processing', 'Completed', 'Cancelled', 'Delivered'],
            state='readonly',
            width=12
        )
        self.order_status_filter.set('All')
        self.order_status_filter.pack(side='left', padx=(0, 15))
        self.order_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_order_payments_trace())
        
        # Invoice status filter
        tk.Label(
            control_frame,
            text="Invoice Status:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(10, 10))
        
        self.invoice_status_filter = ttk.Combobox(
            control_frame,
            values=['All', 'Unpaid', 'Partial', 'Paid', 'Overdue'],
            state='readonly',
            width=12
        )
        self.invoice_status_filter.set('All')
        self.invoice_status_filter.pack(side='left', padx=(0, 15))
        self.invoice_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_order_payments_trace())
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_order_payments_trace
        )
        refresh_btn.pack(side='right')
        
        # Treeview frame
        tree_frame = tk.Frame(self.order_payments_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('Order ID', 'Order No', 'Resident', 'Order Status', 
                   'Invoice Amount', 'Invoice Status', 'Payment Amount', 'Payment Method')
        self.order_payments_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Define headings
        self.order_payments_tree.heading('Order ID', text='Order ID')
        self.order_payments_tree.heading('Order No', text='Order No')
        self.order_payments_tree.heading('Resident', text='Resident')
        self.order_payments_tree.heading('Order Status', text='Order Status')
        self.order_payments_tree.heading('Invoice Amount', text='Invoice Amount')
        self.order_payments_tree.heading('Invoice Status', text='Invoice Status')
        self.order_payments_tree.heading('Payment Amount', text='Payment Amount')
        self.order_payments_tree.heading('Payment Method', text='Payment Method')
        
        # Define column widths
        self.order_payments_tree.column('Order ID', width=70, anchor='center')
        self.order_payments_tree.column('Order No', width=100, anchor='center')
        self.order_payments_tree.column('Resident', width=150)
        self.order_payments_tree.column('Order Status', width=120, anchor='center')
        self.order_payments_tree.column('Invoice Amount', width=120, anchor='center')
        self.order_payments_tree.column('Invoice Status', width=120, anchor='center')
        self.order_payments_tree.column('Payment Amount', width=120, anchor='center')
        self.order_payments_tree.column('Payment Method', width=120, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.order_payments_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.order_payments_tree.xview)
        self.order_payments_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.order_payments_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tags for status colors
        self.order_payments_tree.tag_configure('Completed', foreground=self.COLORS['success'])
        self.order_payments_tree.tag_configure('Pending', foreground=self.COLORS['warning'])
        self.order_payments_tree.tag_configure('Paid', foreground=self.COLORS['success'])
        self.order_payments_tree.tag_configure('Unpaid', foreground=self.COLORS['danger'])
        
    def load_order_payments_trace(self):
        """Loads order payments trace data."""
        # Clear existing items
        for item in self.order_payments_tree.get_children():
            self.order_payments_tree.delete(item)
            
        order_status = self.order_status_filter.get()
        invoice_status = self.invoice_status_filter.get()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT
                    o.order_id,
                    o.order_number,
                    r.full_name as resident_name,
                    o.status as order_status,
                    i.total_amount as invoice_amount,
                    i.status as invoice_status,
                    COALESCE(p.amount, 0) as payment_amount,
                    p.payment_method
                FROM Orders o
                JOIN Resident r ON o.resident_id = r.resident_id
                LEFT JOIN Invoice i ON o.order_id = i.order_id
                LEFT JOIN Payments p ON i.invoice_id = p.invoice_id
                WHERE 1=1
            """
            params = []
            
            if order_status != 'All':
                query += " AND o.status = ?"
                params.append(order_status)
                
            if invoice_status != 'All':
                query += " AND i.status = ?"
                params.append(invoice_status)
                
            query += " ORDER BY o.order_id DESC, p.payment_date"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                self.order_payments_tree.insert('', 'end', values=(
                    row['order_id'],
                    row['order_number'],
                    row['resident_name'],
                    row['order_status'],
                    format_currency(row['invoice_amount']),
                    row['invoice_status'] if row['invoice_status'] else 'No Invoice',
                    format_currency(row['payment_amount']) if row['payment_amount'] > 0 else '-',
                    row['payment_method'] if row['payment_method'] else '-'
                ), tags=(row['order_status'], row['invoice_status']))
                
            self.update_last_updated()
            
        except Exception as e:
            print(f"[ReportsWindow] Error loading order payments trace: {e}")
            show_error(f"Failed to load order payments trace: {str(e)}")
        finally:
            close_connection(conn)
            
    # ==============================================
    # TAB 3: STAFF WORKLOAD
    # ==============================================
    
    def create_staff_workload_tab(self):
        """Creates the Staff Workload report tab."""
        # Control frame
        control_frame = tk.Frame(self.staff_workload_frame, bg=self.COLORS['bg'])
        control_frame.pack(fill='x', pady=(0, 15))
        
        # Role filter
        tk.Label(
            control_frame,
            text="Role:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(0, 10))
        
        self.role_filter = ttk.Combobox(
            control_frame,
            values=['All', 'Washer', 'Dryer', 'Ironer', 'Packer', 'Delivery', 'Admin'],
            state='readonly',
            width=12
        )
        self.role_filter.set('All')
        self.role_filter.pack(side='left', padx=(0, 15))
        self.role_filter.bind('<<ComboboxSelected>>', lambda e: self.load_staff_workload())
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_staff_workload
        )
        refresh_btn.pack(side='right')
        
        # Treeview frame
        tree_frame = tk.Frame(self.staff_workload_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('Staff ID', 'Name', 'Role', 'Orders Managed', 'Tracking Records', 'Status')
        self.staff_workload_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Define headings
        self.staff_workload_tree.heading('Staff ID', text='Staff ID')
        self.staff_workload_tree.heading('Name', text='Staff Name')
        self.staff_workload_tree.heading('Role', text='Role')
        self.staff_workload_tree.heading('Orders Managed', text='Orders Managed')
        self.staff_workload_tree.heading('Tracking Records', text='Tracking Records')
        self.staff_workload_tree.heading('Status', text='Status')
        
        # Define column widths
        self.staff_workload_tree.column('Staff ID', width=70, anchor='center')
        self.staff_workload_tree.column('Name', width=180)
        self.staff_workload_tree.column('Role', width=120, anchor='center')
        self.staff_workload_tree.column('Orders Managed', width=120, anchor='center')
        self.staff_workload_tree.column('Tracking Records', width=130, anchor='center')
        self.staff_workload_tree.column('Status', width=100, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.staff_workload_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.staff_workload_tree.xview)
        self.staff_workload_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.staff_workload_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tags
        self.staff_workload_tree.tag_configure('Available', foreground=self.COLORS['success'])
        self.staff_workload_tree.tag_configure('Unavailable', foreground=self.COLORS['danger'])
        
    def load_staff_workload(self):
        """Loads staff workload data."""
        # Clear existing items
        for item in self.staff_workload_tree.get_children():
            self.staff_workload_tree.delete(item)
            
        role_filter = self.role_filter.get()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    s.staff_id,
                    s.full_name,
                    s.role,
                    s.is_available,
                    COUNT(DISTINCT o.order_id) as orders_managed,
                    COUNT(DISTINCT t.tracking_id) as tracking_records
                FROM Staff s
                LEFT JOIN Orders o ON s.staff_id = o.staff_id
                LEFT JOIN Tracking t ON s.staff_id = t.staff_id
                WHERE 1=1
            """
            params = []
            
            if role_filter != 'All':
                query += " AND s.role = ?"
                params.append(role_filter)
                
            query += """
                GROUP BY s.staff_id, s.full_name, s.role, s.is_available
                ORDER BY s.staff_id
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            for row in rows:
                status_text = "✅ Available" if row['is_available'] == 1 else "❌ Unavailable"
                self.staff_workload_tree.insert('', 'end', values=(
                    row['staff_id'],
                    row['full_name'],
                    row['role'],
                    row['orders_managed'] or 0,
                    row['tracking_records'] or 0,
                    status_text
                ), tags=('Available' if row['is_available'] == 1 else 'Unavailable',))
                
            self.update_last_updated()
            
        except Exception as e:
            print(f"[ReportsWindow] Error loading staff workload: {e}")
            show_error(f"Failed to load staff workload: {str(e)}")
        finally:
            close_connection(conn)
            
    # ==============================================
    # TAB 4: PRINT RECEIPT LOG
    # ==============================================
    
    def create_print_log_tab(self):
        """Creates the Print Receipt Log report tab."""
        # Control frame
        control_frame = tk.Frame(self.print_log_frame, bg=self.COLORS['bg'])
        control_frame.pack(fill='x', pady=(0, 15))
        
        # Date range
        tk.Label(
            control_frame,
            text="From Date:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(0, 10))
        
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.from_date_entry = tk.Entry(
            control_frame,
            textvariable=self.from_date_var,
            font=('Helvetica', 10),
            width=12
        )
        self.from_date_entry.pack(side='left', padx=(0, 15))
        
        tk.Label(
            control_frame,
            text="To Date:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['bg']
        ).pack(side='left', padx=(0, 10))
        
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.to_date_entry = tk.Entry(
            control_frame,
            textvariable=self.to_date_var,
            font=('Helvetica', 10),
            width=12
        )
        self.to_date_entry.pack(side='left', padx=(0, 15))
        
        # Apply filter button
        apply_btn = tk.Button(
            control_frame,
            text="Apply Filter",
            font=('Helvetica', 10),
            bg=self.COLORS['primary'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_print_log
        )
        apply_btn.pack(side='left', padx=(0, 15))
        
        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_print_log
        )
        refresh_btn.pack(side='right')
        
        # Treeview frame
        tree_frame = tk.Frame(self.print_log_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('Receipt No', 'Invoice No', 'Resident', 'Amount', 'Printed By', 'Print Time', 'Copies', 'Status')
        self.print_log_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Define headings
        self.print_log_tree.heading('Receipt No', text='Receipt No')
        self.print_log_tree.heading('Invoice No', text='Invoice No')
        self.print_log_tree.heading('Resident', text='Resident')
        self.print_log_tree.heading('Amount', text='Amount')
        self.print_log_tree.heading('Printed By', text='Printed By')
        self.print_log_tree.heading('Print Time', text='Print Time')
        self.print_log_tree.heading('Copies', text='Copies')
        self.print_log_tree.heading('Status', text='Status')
        
        # Define column widths
        self.print_log_tree.column('Receipt No', width=120, anchor='center')
        self.print_log_tree.column('Invoice No', width=100, anchor='center')
        self.print_log_tree.column('Resident', width=150)
        self.print_log_tree.column('Amount', width=100, anchor='center')
        self.print_log_tree.column('Printed By', width=120)
        self.print_log_tree.column('Print Time', width=150, anchor='center')
        self.print_log_tree.column('Copies', width=60, anchor='center')
        self.print_log_tree.column('Status', width=80, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.print_log_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.print_log_tree.xview)
        self.print_log_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.print_log_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tag for failed prints
        self.print_log_tree.tag_configure('Failed', foreground=self.COLORS['danger'])
        self.print_log_tree.tag_configure('Success', foreground=self.COLORS['success'])
        
    def load_print_log(self):
        """Loads print receipt log data."""
        # Clear existing items
        for item in self.print_log_tree.get_children():
            self.print_log_tree.delete(item)
            
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    pr.receipt_number,
                    i.invoice_number,
                    r.full_name as resident_name,
                    i.total_amount,
                    pr.printed_by,
                    pr.print_time,
                    pr.copies,
                    pr.status
                FROM Print pr
                JOIN Invoice i ON pr.invoice_id = i.invoice_id
                JOIN Orders o ON i.order_id = o.order_id
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE date(pr.print_time) BETWEEN ? AND ?
                ORDER BY pr.print_time DESC
            """
            
            cursor.execute(query, (from_date, to_date))
            rows = cursor.fetchall()
            
            for row in rows:
                self.print_log_tree.insert('', 'end', values=(
                    row['receipt_number'],
                    row['invoice_number'],
                    row['resident_name'],
                    format_currency(row['total_amount']),
                    row['printed_by'],
                    row['print_time'][:19] if row['print_time'] else '-',
                    row['copies'],
                    row['status']
                ), tags=(row['status'],))
                
            self.update_last_updated()
            
        except Exception as e:
            print(f"[ReportsWindow] Error loading print log: {e}")
            show_error(f"Failed to load print log: {str(e)}")
        finally:
            close_connection(conn)
            
    # ==============================================
    # UTILITY FUNCTIONS
    # ==============================================
    
    def load_all_reports(self):
        """Loads all report tabs."""
        self.load_monthly_summary()
        self.load_order_payments_trace()
        self.load_staff_workload()
        self.load_print_log()
        
    def update_last_updated(self):
        """Updates the last updated timestamp."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated_label.config(text=f"Last Updated: {current_time}")


# ==============================================
# TEST BLOCK (for standalone testing)
# ==============================================

if __name__ == "__main__":
    from database import get_connection, close_connection
    from schema import create_tables
    from seed_data import seed_all
    from auth import login_user
    
    # Initialize database
    print("Initializing database...")
    create_tables()
    seed_all()
    
    # Create root window
    root = tk.Tk()
    root.title("TeddyShine Laundry Management System - Reports")
    root.geometry("1300x700")
    root.configure(bg='#E8F0E6')
    
    # Center window
    center_window(root, 1300, 700)
    
    # Test login as admin
    login_user("admin@teddyshine.com", "admin123")
    
    # Dummy callback
    def go_back():
        print("Going back to dashboard...")
        root.quit()
    
    # Create and show reports window
    reports_window = ReportsWindow(root, go_back)
    reports_window.pack(fill='both', expand=True)
    
    root.mainloop()