"""
TeddyShine Laundry Management System - Invoice Window Module
Color Theme: Light Greenish-Gray (#E8F0E6 background style)
Module: invoice_window.py
Purpose: Generate and view invoices for orders
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database import get_connection, close_connection
from auth import get_current_user
from helpers import (
    show_error, show_success, show_confirm, center_window,
    format_date, format_currency, safe_float, safe_int,
    get_current_date, get_current_datetime
)


class InvoiceWindow(tk.Frame):
    """
    Invoice Window - Generate and view invoices for orders.
    Provides tabs for Invoice Generation and Invoice Viewing.
    """
    
    COLORS = {
        'bg': '#E8F0E6',
        'card_bg': '#FFFFFF',
        'primary': '#2E7D32',
        'primary_dark': '#1B5E20',
        'primary_light': '#4CAF50',
        'accent': '#81C784',
        'text': '#1B5E20',
        'text_secondary': '#555555',
        'text_light': '#FFFFFF',
        'border': '#C8E6C9',
        'danger': '#F44336',
        'danger_dark': '#D32F2F',
        'warning': '#FF9800',
        'success': '#4CAF50',
        'info': '#2196F3',
        'header_bg': '#F5F9F4',
        'paid_bg': '#E8F5E9',
        'partial_bg': '#FFF3E0',
        'unpaid_bg': '#FFEBEE'
    }
    
    INVOICE_STATUS = ['All', 'Unpaid', 'Partial', 'Paid', 'Overdue']
    
    def __init__(self, parent, go_back_callback):
        super().__init__(parent, bg=self.COLORS['bg'])
        self.parent = parent
        self.go_back_callback = go_back_callback
        self.current_invoice_id = None
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        self.create_main_content()
        
        self.load_orders_without_invoice()
        self.load_invoices()
        
    def create_header(self):
        header_frame = tk.Frame(
            self,
            bg=self.COLORS['primary'],
            height=70
        )
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)
        
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
        
        def on_enter(e):
            back_btn.config(bg=self.COLORS['primary'])
            
        def on_leave(e):
            back_btn.config(bg=self.COLORS['primary_dark'])
            
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        title_label = tk.Label(
            header_frame,
            text="Invoice Management",
            font=('Helvetica', 20, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15)
        
        self.stats_label = tk.Label(
            header_frame,
            text="Total Invoices: 0",
            font=('Helvetica', 11),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_light']
        )
        self.stats_label.grid(row=0, column=2, padx=20, pady=15, sticky='e')
        
    def create_main_content(self):
        main_container = tk.Frame(self, bg=self.COLORS['bg'])
        main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Helvetica', 11))
        
        self.generate_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.generate_frame, text="📄 Generate Invoice")
        self.create_generate_tab()
        
        self.view_frame = tk.Frame(self.notebook, bg=self.COLORS['bg'])
        self.notebook.add(self.view_frame, text="📋 View Invoices")
        self.create_view_tab()
        
    def create_generate_tab(self):
        main_frame = tk.Frame(self.generate_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        left_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        right_panel = tk.Frame(main_frame, bg=self.COLORS['bg'])
        right_panel.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        self.create_order_selection_panel(left_panel)
        self.create_invoice_preview_panel(right_panel)
        
    def create_order_selection_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        card.pack(fill='both', expand=True)
        
        title_frame = tk.Frame(card, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            title_frame,
            text="📦 Select Order",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        form_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        form_frame.pack(fill='both', padx=20, pady=20)
        
        tk.Label(
            form_frame,
            text="Order *:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.order_combo = ttk.Combobox(
            form_frame,
            font=('Helvetica', 11),
            state='readonly',
            width=35
        )
        self.order_combo.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15), ipady=5)
        self.order_combo.bind('<<ComboboxSelected>>', self.on_order_select)
        
        tk.Label(
            form_frame,
            text="Resident:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        self.resident_label = tk.Label(
            form_frame,
            text="-",
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary'],
            anchor='w'
        )
        self.resident_label.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        tk.Label(
            form_frame,
            text="Order Amount:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=4, column=0, sticky='w', pady=(0, 5))
        
        self.amount_label = tk.Label(
            form_frame,
            text="₹ 0.00",
            font=('Helvetica', 13, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['primary']
        )
        self.amount_label.grid(row=5, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        tk.Label(
            form_frame,
            text="Discount (₹):",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        self.discount_var = tk.StringVar(value="0")
        self.discount_var.trace('w', self.update_final_amount)
        
        self.discount_entry = tk.Entry(
            form_frame,
            textvariable=self.discount_var,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        self.discount_entry.grid(row=7, column=0, sticky='w', pady=(0, 15), ipady=5)
        
        tk.Label(
            form_frame,
            text="Final Amount:",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=8, column=0, sticky='w', pady=(0, 5))
        
        self.final_amount_label = tk.Label(
            form_frame,
            text="₹ 0.00",
            font=('Helvetica', 16, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['success']
        )
        self.final_amount_label.grid(row=9, column=0, columnspan=2, sticky='w', pady=(0, 15))
        
        tk.Label(
            form_frame,
            text="Invoice Date:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=10, column=0, sticky='w', pady=(0, 5))
        
        self.invoice_date_var = tk.StringVar(value=get_current_date())
        self.invoice_date_entry = tk.Entry(
            form_frame,
            textvariable=self.invoice_date_var,
            font=('Helvetica', 11),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        self.invoice_date_entry.grid(row=11, column=0, sticky='w', pady=(0, 20), ipady=5)
        
        tk.Label(
            form_frame,
            text="Due Date:",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text']
        ).grid(row=12, column=0, sticky='w', pady=(0, 5))
        
        self.due_date_label = tk.Label(
            form_frame,
            text="-",
            font=('Helvetica', 11),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        self.due_date_label.grid(row=13, column=0, columnspan=2, sticky='w', pady=(0, 20))
        
        self.generate_btn = tk.Button(
            form_frame,
            text="✅ Generate Invoice",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['success'],
            fg='white',
            activebackground='#45A049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.generate_invoice
        )
        self.generate_btn.grid(row=14, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=0)
        
    def create_invoice_preview_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=self.COLORS['card_bg'],
            relief='flat',
            highlightbackground=self.COLORS['border'],
            highlightthickness=1
        )
        card.pack(fill='both', expand=True)
        
        title_frame = tk.Frame(card, bg=self.COLORS['header_bg'])
        title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            title_frame,
            text="🖨️ Invoice Preview",
            font=('Helvetica', 14, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=12)
        
        self.preview_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        self.preview_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.preview_label = tk.Label(
            self.preview_frame,
            text="Select an order to preview invoice",
            font=('Helvetica', 11, 'italic'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_secondary']
        )
        self.preview_label.pack(expand=True)
        
    def create_view_tab(self):
        main_frame = tk.Frame(self.view_frame, bg=self.COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        filter_frame = tk.Frame(main_frame, bg=self.COLORS['card_bg'], relief='flat')
        filter_frame.pack(fill='x', pady=(0, 15), ipady=10)
        
        tk.Label(
            filter_frame,
            text="Filter by Status:",
            font=('Helvetica', 10, 'bold'),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(15, 10))
        
        self.status_filter = ttk.Combobox(
            filter_frame,
            values=self.INVOICE_STATUS,
            state='readonly',
            width=15
        )
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(0, 15))
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_invoices())
        
        tk.Label(
            filter_frame,
            text="Search:",
            font=('Helvetica', 10),
            bg=self.COLORS['card_bg']
        ).pack(side='left', padx=(10, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_invoices())
        
        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=('Helvetica', 10),
            bg='#FAFAFA',
            relief='solid',
            bd=1,
            width=20
        )
        search_entry.pack(side='left', fill='x', expand=True, ipady=5)
        
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 Refresh",
            font=('Helvetica', 10),
            bg=self.COLORS['info'],
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5,
            command=self.load_invoices
        )
        refresh_btn.pack(side='right', padx=15)
        
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Invoice No', 'Order No', 'Resident', 'Total', 'Discount', 'Final', 'Paid', 'Balance', 'Status')
        self.invoice_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=14)
        
        self.invoice_tree.heading('ID', text='ID')
        self.invoice_tree.heading('Invoice No', text='Invoice No')
        self.invoice_tree.heading('Order No', text='Order No')
        self.invoice_tree.heading('Resident', text='Resident')
        self.invoice_tree.heading('Total', text='Total')
        self.invoice_tree.heading('Discount', text='Discount')
        self.invoice_tree.heading('Final', text='Final')
        self.invoice_tree.heading('Paid', text='Paid')
        self.invoice_tree.heading('Balance', text='Balance')
        self.invoice_tree.heading('Status', text='Status')
        
        self.invoice_tree.column('ID', width=50, anchor='center')
        self.invoice_tree.column('Invoice No', width=100, anchor='center')
        self.invoice_tree.column('Order No', width=100, anchor='center')
        self.invoice_tree.column('Resident', width=150)
        self.invoice_tree.column('Total', width=90, anchor='center')
        self.invoice_tree.column('Discount', width=90, anchor='center')
        self.invoice_tree.column('Final', width=90, anchor='center')
        self.invoice_tree.column('Paid', width=90, anchor='center')
        self.invoice_tree.column('Balance', width=90, anchor='center')
        self.invoice_tree.column('Status', width=100, anchor='center')
        
        self.invoice_tree.tag_configure('paid', background=self.COLORS['paid_bg'])
        self.invoice_tree.tag_configure('partial', background=self.COLORS['partial_bg'])
        self.invoice_tree.tag_configure('unpaid', background=self.COLORS['unpaid_bg'])
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.invoice_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.invoice_tree.xview)
        self.invoice_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.invoice_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.invoice_tree.bind('<<TreeviewSelect>>', self.on_invoice_select)
        
        action_frame = tk.Frame(main_frame, bg=self.COLORS['bg'])
        action_frame.pack(fill='x', pady=(15, 0))
        
        self.print_btn = tk.Button(
            action_frame,
            text="🖨️ Print Receipt",
            font=('Helvetica', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            state='disabled',
            command=self.print_receipt
        )
        self.print_btn.pack(side='left', padx=5)
        
        view_details_btn = tk.Button(
            action_frame,
            text="📄 View Details",
            font=('Helvetica', 11),
            bg=self.COLORS['info'],
            fg='white',
            activebackground='#1976D2',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.view_invoice_details
        )
        view_details_btn.pack(side='left', padx=5)
        
    def load_orders_without_invoice(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, o.order_number, r.full_name, o.final_amount
                FROM Orders o
                JOIN Resident r ON o.resident_id = r.resident_id
                LEFT JOIN Invoice i ON o.order_id = i.order_id
                WHERE i.invoice_id IS NULL AND o.status != 'Cancelled'
                ORDER BY o.order_id DESC
            """)
            orders = cursor.fetchall()
            
            self.order_list = []
            for o in orders:
                display_text = f"{o['order_number']} - {o['full_name']} (₹{o['final_amount']})"
                self.order_list.append({
                    'id': o['order_id'],
                    'number': o['order_number'],
                    'resident': o['full_name'],
                    'amount': o['final_amount'],
                    'display': display_text
                })
            
            self.order_combo['values'] = [o['display'] for o in self.order_list]
            
        except Exception as e:
            print(f"[InvoiceWindow] Error loading orders: {e}")
        finally:
            close_connection(conn)
            
    def on_order_select(self, event=None):
        selection = self.order_combo.current()
        if selection < 0:
            return
            
        order = self.order_list[selection]
        
        self.resident_label.config(text=order['resident'])
        self.amount_label.config(text=format_currency(order['amount']))
        
        self.discount_var.set("0")
        
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.due_date_label.config(text=format_date(due_date))
        
        self.update_preview(order)
        
    def update_preview(self, order):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
            
        discount = safe_float(self.discount_var.get())
        final_amount = order['amount'] - discount
        
        preview_card = tk.Frame(self.preview_frame, bg=self.COLORS['header_bg'], relief='solid', bd=1)
        preview_card.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            preview_card,
            text="TEDDYSHINE LAUNDRY",
            font=('Helvetica', 16, 'bold'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['primary']
        ).pack(pady=(15, 5))
        
        tk.Label(
            preview_card,
            text="Laundry Management System",
            font=('Helvetica', 10),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['text_secondary']
        ).pack()
        
        tk.Label(
            preview_card,
            text="=" * 40,
            font=('Helvetica', 10),
            bg=self.COLORS['header_bg']
        ).pack(pady=10)
        
        details_frame = tk.Frame(preview_card, bg=self.COLORS['header_bg'])
        details_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(details_frame, text=f"Order No:", font=('Helvetica', 10, 'bold'),
                bg=self.COLORS['header_bg']).grid(row=0, column=0, sticky='w')
        tk.Label(details_frame, text=order['number'], font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        tk.Label(details_frame, text=f"Resident:", font=('Helvetica', 10, 'bold'),
                bg=self.COLORS['header_bg']).grid(row=1, column=0, sticky='w', pady=(5, 0))
        tk.Label(details_frame, text=order['resident'], font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=1, column=1, sticky='w', padx=(10, 0), pady=(5, 0))
        
        tk.Label(details_frame, text=f"Date:", font=('Helvetica', 10, 'bold'),
                bg=self.COLORS['header_bg']).grid(row=2, column=0, sticky='w', pady=(5, 0))
        tk.Label(details_frame, text=format_date(get_current_date()), font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=2, column=1, sticky='w', padx=(10, 0), pady=(5, 0))
        
        tk.Label(details_frame, text=f"Due Date:", font=('Helvetica', 10, 'bold'),
                bg=self.COLORS['header_bg']).grid(row=3, column=0, sticky='w', pady=(5, 0))
        tk.Label(details_frame, text=self.due_date_label.cget('text'), font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=3, column=1, sticky='w', padx=(10, 0), pady=(5, 0))
        
        tk.Label(
            preview_card,
            text="=" * 40,
            font=('Helvetica', 10),
            bg=self.COLORS['header_bg']
        ).pack(pady=10)
        
        summary_frame = tk.Frame(preview_card, bg=self.COLORS['header_bg'])
        summary_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Label(summary_frame, text=f"Subtotal:", font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=0, column=0, sticky='w')
        tk.Label(summary_frame, text=format_currency(order['amount']), font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=0, column=1, sticky='e', padx=(20, 0))
        
        tk.Label(summary_frame, text=f"Discount:", font=('Helvetica', 10),
                bg=self.COLORS['header_bg']).grid(row=1, column=0, sticky='w', pady=(5, 0))
        tk.Label(summary_frame, text=f"- {format_currency(discount)}", font=('Helvetica', 10),
                bg=self.COLORS['header_bg'], fg=self.COLORS['danger'] if discount > 0 else 'black'
                ).grid(row=1, column=1, sticky='e', padx=(20, 0), pady=(5, 0))
        
        tk.Label(
            preview_card,
            text="-" * 40,
            font=('Helvetica', 10),
            bg=self.COLORS['header_bg']
        ).pack(pady=5)
        
        tk.Label(summary_frame, text=f"TOTAL:", font=('Helvetica', 12, 'bold'),
                bg=self.COLORS['header_bg'], fg=self.COLORS['primary']).grid(row=2, column=0, sticky='w', pady=(5, 0))
        tk.Label(summary_frame, text=format_currency(final_amount), font=('Helvetica', 12, 'bold'),
                bg=self.COLORS['header_bg'], fg=self.COLORS['primary']).grid(row=2, column=1, sticky='e', padx=(20, 0), pady=(5, 0))
        
        tk.Label(
            preview_card,
            text="=" * 40,
            font=('Helvetica', 10),
            bg=self.COLORS['header_bg']
        ).pack(pady=10)
        
        tk.Label(
            preview_card,
            text="Thank you for your business!",
            font=('Helvetica', 9, 'italic'),
            bg=self.COLORS['header_bg'],
            fg=self.COLORS['text_secondary']
        ).pack(pady=(5, 15))
        
    def update_final_amount(self, *args):
        selection = self.order_combo.current()
        if selection < 0:
            return
            
        order = self.order_list[selection]
        discount = safe_float(self.discount_var.get())
        
        if discount < 0:
            self.discount_var.set("0")
            discount = 0
            
        if discount > order['amount']:
            self.discount_var.set(str(order['amount']))
            discount = order['amount']
            
        final_amount = order['amount'] - discount
        self.final_amount_label.config(text=format_currency(final_amount))
        
        if selection >= 0:
            self.update_preview(order)
            
    def generate_invoice(self):
        selection = self.order_combo.current()
        if selection < 0:
            show_error("Please select an order")
            return
            
        order = self.order_list[selection]
        discount = safe_float(self.discount_var.get())
        final_amount = order['amount'] - discount
        invoice_date = self.invoice_date_var.get()
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Invoice (order_id, invoice_number, subtotal, discount_amount,
                                    total_amount, amount_paid, balance_due, status,
                                    generated_date, due_date)
                VALUES (?, ?, ?, ?, ?, 0, ?, 'Unpaid', ?, ?)
            """, (order['id'], invoice_number, order['amount'], discount,
                  final_amount, final_amount, invoice_date, due_date))
            conn.commit()
            
            show_success(f"Invoice {invoice_number} generated successfully!\nFinal Amount: {format_currency(final_amount)}")
            
            self.order_combo.set('')
            self.resident_label.config(text="-")
            self.amount_label.config(text="₹ 0.00")
            self.discount_var.set("0")
            self.final_amount_label.config(text="₹ 0.00")
            self.due_date_label.config(text="-")
            
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            self.preview_label = tk.Label(
                self.preview_frame,
                text="Select an order to preview invoice",
                font=('Helvetica', 11, 'italic'),
                bg=self.COLORS['card_bg'],
                fg=self.COLORS['text_secondary']
            )
            self.preview_label.pack(expand=True)
            
            self.load_orders_without_invoice()
            self.load_invoices()
            
            self.notebook.select(1)
            
        except Exception as e:
            print(f"[InvoiceWindow] Error generating invoice: {e}")
            show_error(f"Failed to generate invoice: {str(e)}")
            conn.rollback()
        finally:
            close_connection(conn)
            
    def load_invoices(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
            
        status_filter = self.status_filter.get()
        search_term = self.search_var.get().strip()
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT i.invoice_id, i.invoice_number, o.order_number, r.full_name,
                       i.subtotal, i.discount_amount, i.total_amount, i.amount_paid,
                       i.balance_due, i.status
                FROM Invoice i
                JOIN Orders o ON i.order_id = o.order_id
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE 1=1
            """
            params = []
            
            if status_filter != 'All':
                query += " AND i.status = ?"
                params.append(status_filter)
                
            if search_term:
                query += " AND (i.invoice_number LIKE ? OR o.order_number LIKE ? OR r.full_name LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
                
            query += " ORDER BY i.invoice_id DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            status_info = {
                'Paid': {'emoji': '✅', 'tag': 'paid'},
                'Partial': {'emoji': '⚠️', 'tag': 'partial'},
                'Unpaid': {'emoji': '❌', 'tag': 'unpaid'},
                'Overdue': {'emoji': '🔴', 'tag': 'unpaid'}
            }
            
            for row in rows:
                info = status_info.get(row['status'], {'emoji': '❓', 'tag': 'unpaid'})
                display_status = f"{info['emoji']} {row['status']}"
                
                self.invoice_tree.insert('', 'end', values=(
                    row['invoice_id'],
                    row['invoice_number'],
                    row['order_number'],
                    row['full_name'],
                    format_currency(row['subtotal']),
                    format_currency(row['discount_amount']),
                    format_currency(row['total_amount']),
                    format_currency(row['amount_paid']),
                    format_currency(row['balance_due']),
                    display_status
                ), tags=(info['tag'],))
                
            self.stats_label.config(text=f"Total Invoices: {len(rows)}")
            
        except Exception as e:
            print(f"[InvoiceWindow] Error loading invoices: {e}")
            show_error(f"Failed to load invoices: {str(e)}")
        finally:
            close_connection(conn)
            
    def on_invoice_select(self, event):
        selected = self.invoice_tree.selection()
        if selected:
            self.print_btn.config(state='normal')
            values = self.invoice_tree.item(selected[0], 'values')
            if values:
                self.current_invoice_id = safe_int(values[0])
        else:
            self.print_btn.config(state='disabled')
            self.current_invoice_id = None
            
    def print_receipt(self):
        if not self.current_invoice_id:
            show_error("Please select an invoice")
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT i.*, o.order_number, r.full_name, r.phone, r.block_name, r.room_number
                FROM Invoice i
                JOIN Orders o ON i.order_id = o.order_id
                JOIN Resident r ON o.resident_id = r.resident_id
                WHERE i.invoice_id = ?
            """, (self.current_invoice_id,))
            invoice = cursor.fetchone()
            
            if not invoice:
                show_error("Invoice not found")
                return
                
            receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            current_user = get_current_user()
            printed_by = current_user.get('name', 'System')
            printed_by_id = current_user.get('user_id', 0)
            
            cursor.execute("""
                INSERT INTO Print (invoice_id, receipt_number, printed_by, printed_by_id,
                                  print_time, copies, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Success')
            """, (self.current_invoice_id, receipt_number, printed_by, printed_by_id,
                  get_current_datetime(), 1))
            conn.commit()
            
            self.show_receipt_popup(invoice, receipt_number)
            
            show_success(f"Receipt {receipt_number} printed successfully!")
            
        except Exception