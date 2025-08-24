"""
Excel Automation Module
Provides comprehensive Excel automation capabilities including:
- Opening Excel files
- Navigating through worksheets
- Reading and writing data
- Formatting cells
- Creating charts and graphs
- Data analysis and manipulation
"""

import os
import time
import subprocess
import pyautogui
import pandas as pd
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import win32com.client
from typing import Optional, Tuple, List, Dict, Any
import re

# Import screen vision capabilities
try:
    from Backend.ScreenVision import capture_and_analyze, get_smart_click_position, start_screen_monitoring
    SCREEN_VISION_AVAILABLE = True
    print("🖥️ Excel Automation: Screen Vision System loaded successfully")
except ImportError as e:
    print(f"⚠️ Excel Automation: Screen Vision not available: {e}")
    SCREEN_VISION_AVAILABLE = False

class ExcelAutomation:
    """Main Excel automation class"""
    
    def __init__(self):
        self.excel_app = None
        self.workbook = None
        self.current_file = None
        self.current_sheet = None
        self.last_action = None
        
    def open_excel_file(self, file_path: str) -> str:
        """
        Open an Excel file using multiple methods
        """
        try:
            print(f"📊 Opening Excel file: {file_path}")
            
            # Method 1: Try using win32com (most reliable for automation)
            try:
                self.excel_app = win32com.client.Dispatch("Excel.Application")
                self.excel_app.Visible = True
                self.workbook = self.excel_app.Workbooks.Open(file_path)
                self.current_file = file_path
                print(f"✅ Excel file opened successfully via COM: {file_path}")
                return f"Opened Excel file: {os.path.basename(file_path)}"
            except Exception as e:
                print(f"COM method failed: {e}")
            
            # Method 2: Try using os.startfile
            try:
                os.startfile(file_path)
                time.sleep(3)  # Wait for Excel to load
                self.current_file = file_path
                print(f"✅ Excel file opened successfully via startfile: {file_path}")
                return f"Opened Excel file: {os.path.basename(file_path)}"
            except Exception as e:
                print(f"Startfile method failed: {e}")
            
            # Method 3: Try using subprocess
            try:
                subprocess.run(["start", file_path], shell=True)
                time.sleep(3)
                self.current_file = file_path
                print(f"✅ Excel file opened successfully via subprocess: {file_path}")
                return f"Opened Excel file: {os.path.basename(file_path)}"
            except Exception as e:
                print(f"Subprocess method failed: {e}")
            
            return f"Failed to open Excel file: {file_path}"
            
        except Exception as e:
            print(f"❌ Error opening Excel file: {e}")
            return f"Error opening Excel file: {str(e)}"
    
    def create_new_workbook(self) -> str:
        """Create a new Excel workbook"""
        try:
            # Method 1: Using COM
            try:
                self.excel_app = win32com.client.Dispatch("Excel.Application")
                self.excel_app.Visible = True
                self.workbook = self.excel_app.Workbooks.Add()
                print("✅ New Excel workbook created via COM")
                return "Created new Excel workbook"
            except Exception as e:
                print(f"COM method failed: {e}")
            
            # Method 2: Using openpyxl
            try:
                wb = Workbook()
                default_sheet = wb.active
                default_sheet.title = "Sheet1"
                
                # Save to a temporary location
                temp_path = os.path.join(os.getcwd(), "temp_workbook.xlsx")
                wb.save(temp_path)
                wb.close()
                
                # Open the saved file
                return self.open_excel_file(temp_path)
            except Exception as e:
                print(f"Openpyxl method failed: {e}")
            
            return "Failed to create new workbook"
            
        except Exception as e:
            print(f"❌ Error creating workbook: {e}")
            return f"Error creating workbook: {str(e)}"
    
    def navigate_to_cell(self, cell_reference: str) -> str:
        """
        Navigate to a specific cell in Excel
        Examples: "A1", "B5", "C10"
        """
        try:
            print(f"🎯 Navigating to cell: {cell_reference}")
            
            # Method 1: Using COM
            if self.excel_app and self.workbook:
                try:
                    active_sheet = self.workbook.ActiveSheet
                    active_sheet.Range(cell_reference).Select()
                    print(f"✅ Navigated to cell {cell_reference} via COM")
                    return f"Navigated to cell {cell_reference}"
                except Exception as e:
                    print(f"COM navigation failed: {e}")
            
            # Method 2: Using keyboard shortcuts
            try:
                # Press F5 to open Go To dialog
                pyautogui.press('f5')
                time.sleep(0.5)
                
                # Type the cell reference
                pyautogui.write(cell_reference)
                time.sleep(0.5)
                
                # Press Enter
                pyautogui.press('enter')
                time.sleep(0.5)
                
                print(f"✅ Navigated to cell {cell_reference} via keyboard")
                return f"Navigated to cell {cell_reference}"
            except Exception as e:
                print(f"Keyboard navigation failed: {e}")
            
            # Method 3: Using screen vision (if available)
            if SCREEN_VISION_AVAILABLE:
                try:
                    # Analyze screen to find Excel interface
                    analysis = capture_and_analyze(f"excel interface with cell {cell_reference}")
                    
                    # Try to find and click on the cell
                    click_pos = get_smart_click_position(f"cell {cell_reference} in excel")
                    if click_pos:
                        x, y = click_pos
                        pyautogui.click(x, y)
                        print(f"✅ Navigated to cell {cell_reference} via screen vision")
                        return f"Navigated to cell {cell_reference}"
                except Exception as e:
                    print(f"Screen vision navigation failed: {e}")
            
            return f"Could not navigate to cell {cell_reference}"
            
        except Exception as e:
            print(f"❌ Error navigating to cell: {e}")
            return f"Error navigating to cell: {str(e)}"
    
    def enter_data_in_cell(self, cell_reference: str, data: str) -> str:
        """
        Enter data in a specific cell
        """
        try:
            print(f"📝 Entering data '{data}' in cell {cell_reference}")
            
            # First navigate to the cell
            self.navigate_to_cell(cell_reference)
            time.sleep(0.5)
            
            # Enter the data
            pyautogui.write(str(data))
            time.sleep(0.5)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print(f"✅ Entered data '{data}' in cell {cell_reference}")
            return f"Entered '{data}' in cell {cell_reference}"
            
        except Exception as e:
            print(f"❌ Error entering data: {e}")
            return f"Error entering data: {str(e)}"
    
    def read_cell_data(self, cell_reference: str) -> str:
        """
        Read data from a specific cell
        """
        try:
            print(f"📖 Reading data from cell {cell_reference}")
            
            # Method 1: Using COM
            if self.excel_app and self.workbook:
                try:
                    active_sheet = self.workbook.ActiveSheet
                    cell_value = active_sheet.Range(cell_reference).Value
                    print(f"✅ Read data from cell {cell_reference}: {cell_value}")
                    return f"Cell {cell_reference} contains: {cell_value}"
                except Exception as e:
                    print(f"COM read failed: {e}")
            
            # Method 2: Using openpyxl
            if self.current_file and os.path.exists(self.current_file):
                try:
                    wb = load_workbook(self.current_file)
                    ws = wb.active
                    cell_value = ws[cell_reference].value
                    wb.close()
                    print(f"✅ Read data from cell {cell_reference}: {cell_value}")
                    return f"Cell {cell_reference} contains: {cell_value}"
                except Exception as e:
                    print(f"Openpyxl read failed: {e}")
            
            # Method 3: Using screen vision to read visible data
            if SCREEN_VISION_AVAILABLE:
                try:
                    # Navigate to the cell first
                    self.navigate_to_cell(cell_reference)
                    time.sleep(1)
                    
                    # Analyze the screen to read the cell content
                    analysis = capture_and_analyze(f"excel cell {cell_reference} content")
                    print(f"✅ Read data via screen vision: {analysis}")
                    return f"Cell {cell_reference} content: {analysis}"
                except Exception as e:
                    print(f"Screen vision read failed: {e}")
            
            return f"Could not read data from cell {cell_reference}"
            
        except Exception as e:
            print(f"❌ Error reading cell data: {e}")
            return f"Error reading cell data: {str(e)}"
    
    def format_cell(self, cell_reference: str, format_type: str, **kwargs) -> str:
        """
        Format a cell with various formatting options
        format_type: 'bold', 'italic', 'underline', 'color', 'font_size', 'alignment'
        """
        try:
            print(f"🎨 Formatting cell {cell_reference} with {format_type}")
            
            # Navigate to the cell first
            self.navigate_to_cell(cell_reference)
            time.sleep(0.5)
            
            if format_type == 'bold':
                pyautogui.hotkey('ctrl', 'b')
            elif format_type == 'italic':
                pyautogui.hotkey('ctrl', 'i')
            elif format_type == 'underline':
                pyautogui.hotkey('ctrl', 'u')
            elif format_type == 'color':
                # Open format cells dialog
                pyautogui.hotkey('ctrl', '1')
                time.sleep(1)
                # Navigate to font tab and set color
                pyautogui.press('tab')
                pyautogui.press('enter')
            elif format_type == 'font_size':
                size = kwargs.get('size', 12)
                pyautogui.hotkey('ctrl', 'shift', 'p')  # Open font size dialog
                time.sleep(0.5)
                pyautogui.write(str(size))
                pyautogui.press('enter')
            elif format_type == 'alignment':
                alignment = kwargs.get('alignment', 'center')
                if alignment == 'center':
                    pyautogui.hotkey('alt', 'h', 'a', 'c')
                elif alignment == 'left':
                    pyautogui.hotkey('alt', 'h', 'a', 'l')
                elif alignment == 'right':
                    pyautogui.hotkey('alt', 'h', 'a', 'r')
            
            print(f"✅ Formatted cell {cell_reference} with {format_type}")
            return f"Formatted cell {cell_reference} with {format_type}"
            
        except Exception as e:
            print(f"❌ Error formatting cell: {e}")
            return f"Error formatting cell: {str(e)}"
    
    def insert_formula(self, cell_reference: str, formula: str) -> str:
        """
        Insert a formula in a cell
        Examples: "=SUM(A1:A10)", "=AVERAGE(B1:B20)", "=COUNT(C1:C15)"
        """
        try:
            print(f"🧮 Inserting formula '{formula}' in cell {cell_reference}")
            
            # Navigate to the cell
            self.navigate_to_cell(cell_reference)
            time.sleep(0.5)
            
            # Type the formula
            pyautogui.write(formula)
            time.sleep(0.5)
            
            # Press Enter to confirm
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print(f"✅ Inserted formula '{formula}' in cell {cell_reference}")
            return f"Inserted formula '{formula}' in cell {cell_reference}"
            
        except Exception as e:
            print(f"❌ Error inserting formula: {e}")
            return f"Error inserting formula: {str(e)}"
    
    def create_chart(self, chart_type: str, data_range: str, location: str = "A1") -> str:
        """
        Create a chart from data
        chart_type: 'line', 'bar', 'pie', 'column', 'scatter'
        data_range: "A1:B10"
        """
        try:
            print(f"📊 Creating {chart_type} chart from range {data_range}")
            
            # Select the data range
            self.navigate_to_cell(data_range.split(':')[0])
            time.sleep(0.5)
            
            # Extend selection to the full range
            pyautogui.hotkey('ctrl', 'shift', 'end')
            time.sleep(0.5)
            
            # Insert chart
            pyautogui.hotkey('alt', 'n', 'c')  # Insert > Chart
            time.sleep(1)
            
            # Select chart type based on input
            chart_shortcuts = {
                'line': 'l',
                'bar': 'b',
                'pie': 'p',
                'column': 'c',
                'scatter': 's'
            }
            
            if chart_type in chart_shortcuts:
                pyautogui.press(chart_shortcuts[chart_type])
                time.sleep(0.5)
            
            # Press Enter to insert
            pyautogui.press('enter')
            time.sleep(1)
            
            print(f"✅ Created {chart_type} chart from range {data_range}")
            return f"Created {chart_type} chart from range {data_range}"
            
        except Exception as e:
            print(f"❌ Error creating chart: {e}")
            return f"Error creating chart: {str(e)}"
    
    def sort_data(self, range_to_sort: str, sort_by: str, order: str = "ascending") -> str:
        """
        Sort data in a range
        range_to_sort: "A1:C10"
        sort_by: "A" (column to sort by)
        order: "ascending" or "descending"
        """
        try:
            print(f"📈 Sorting range {range_to_sort} by column {sort_by} in {order} order")
            
            # Select the range
            self.navigate_to_cell(range_to_sort.split(':')[0])
            time.sleep(0.5)
            
            # Extend selection
            pyautogui.hotkey('ctrl', 'shift', 'end')
            time.sleep(0.5)
            
            # Open sort dialog
            pyautogui.hotkey('alt', 'd', 's')  # Data > Sort
            time.sleep(1)
            
            # Set sort options
            if order == "descending":
                pyautogui.press('tab')
                pyautogui.press('d')  # Descending
            
            # Press OK
            pyautogui.press('enter')
            time.sleep(0.5)
            
            print(f"✅ Sorted range {range_to_sort} by column {sort_by}")
            return f"Sorted range {range_to_sort} by column {sort_by} in {order} order"
            
        except Exception as e:
            print(f"❌ Error sorting data: {e}")
            return f"Error sorting data: {str(e)}"
    
    def filter_data(self, range_to_filter: str, criteria: str) -> str:
        """
        Apply filter to data
        range_to_filter: "A1:C10"
        criteria: "contains", "equals", "greater than", etc.
        """
        try:
            print(f"🔍 Applying filter to range {range_to_filter} with criteria: {criteria}")
            
            # Select the range
            self.navigate_to_cell(range_to_filter.split(':')[0])
            time.sleep(0.5)
            
            # Extend selection
            pyautogui.hotkey('ctrl', 'shift', 'end')
            time.sleep(0.5)
            
            # Apply filter
            pyautogui.hotkey('ctrl', 'shift', 'l')  # Toggle filter
            time.sleep(1)
            
            print(f"✅ Applied filter to range {range_to_filter}")
            return f"Applied filter to range {range_to_filter}"
            
        except Exception as e:
            print(f"❌ Error applying filter: {e}")
            return f"Error applying filter: {str(e)}"
    
    def save_workbook(self, file_path: Optional[str] = None) -> str:
        """
        Save the current workbook
        """
        try:
            print("💾 Saving workbook")
            
            if file_path:
                # Save as new file
                pyautogui.hotkey('f12')  # Save As
                time.sleep(1)
                pyautogui.write(file_path)
                time.sleep(0.5)
                pyautogui.press('enter')
            else:
                # Save current file
                pyautogui.hotkey('ctrl', 's')
            
            time.sleep(1)
            print("✅ Workbook saved successfully")
            return "Workbook saved successfully"
            
        except Exception as e:
            print(f"❌ Error saving workbook: {e}")
            return f"Error saving workbook: {str(e)}"
    
    def close_workbook(self) -> str:
        """
        Close the current workbook
        """
        try:
            print("📂 Closing workbook")
            
            pyautogui.hotkey('ctrl', 'w')  # Close workbook
            time.sleep(0.5)
            
            # Handle save prompt if it appears
            try:
                pyautogui.press('n')  # Don't save
            except:
                pass
            
            print("✅ Workbook closed successfully")
            return "Workbook closed successfully"
            
        except Exception as e:
            print(f"❌ Error closing workbook: {e}")
            return f"Error closing workbook: {str(e)}"
    
    def switch_worksheet(self, sheet_name: str) -> str:
        """
        Switch to a different worksheet
        """
        try:
            print(f"📄 Switching to worksheet: {sheet_name}")
            
            # Method 1: Using keyboard shortcuts
            try:
                # Press Ctrl + Page Down/Up to navigate sheets
                pyautogui.hotkey('ctrl', 'pageup')  # Try previous sheet
                time.sleep(0.5)
                pyautogui.hotkey('ctrl', 'pagedown')  # Try next sheet
                time.sleep(0.5)
                
                # Or use Alt + W + S to open sheet selector
                pyautogui.hotkey('alt', 'w', 's')
                time.sleep(1)
                pyautogui.write(sheet_name)
                pyautogui.press('enter')
                time.sleep(0.5)
                
                print(f"✅ Switched to worksheet: {sheet_name}")
                return f"Switched to worksheet: {sheet_name}"
            except Exception as e:
                print(f"Keyboard method failed: {e}")
            
            # Method 2: Using screen vision
            if SCREEN_VISION_AVAILABLE:
                try:
                    analysis = capture_and_analyze(f"excel worksheet tabs with {sheet_name}")
                    click_pos = get_smart_click_position(f"worksheet tab {sheet_name}")
                    if click_pos:
                        x, y = click_pos
                        pyautogui.click(x, y)
                        print(f"✅ Switched to worksheet {sheet_name} via screen vision")
                        return f"Switched to worksheet: {sheet_name}"
                except Exception as e:
                    print(f"Screen vision method failed: {e}")
            
            return f"Could not switch to worksheet: {sheet_name}"
            
        except Exception as e:
            print(f"❌ Error switching worksheet: {e}")
            return f"Error switching worksheet: {str(e)}"
    
    def analyze_data(self, range_to_analyze: str) -> str:
        """
        Analyze data in a range and provide insights
        """
        try:
            print(f"📊 Analyzing data in range: {range_to_analyze}")
            
            # Navigate to the range
            self.navigate_to_cell(range_to_analyze.split(':')[0])
            time.sleep(0.5)
            
            # Select the range
            pyautogui.hotkey('ctrl', 'shift', 'end')
            time.sleep(0.5)
            
            # Use screen vision to analyze the data
            if SCREEN_VISION_AVAILABLE:
                try:
                    analysis = capture_and_analyze(f"excel data analysis for range {range_to_analyze}")
                    print(f"✅ Data analysis completed: {analysis}")
                    return f"Data analysis for range {range_to_analyze}: {analysis}"
                except Exception as e:
                    print(f"Screen vision analysis failed: {e}")
            
            # Fallback: Basic analysis using openpyxl
            if self.current_file and os.path.exists(self.current_file):
                try:
                    wb = load_workbook(self.current_file)
                    ws = wb.active
                    
                    # Parse range
                    start_cell, end_cell = range_to_analyze.split(':')
                    start_col = re.match(r'([A-Z]+)', start_cell).group(1)
                    start_row = int(re.match(r'[A-Z]+(\d+)', start_cell).group(1))
                    end_col = re.match(r'([A-Z]+)', end_cell).group(1)
                    end_row = int(re.match(r'[A-Z]+(\d+)', end_cell).group(1))
                    
                    # Collect data
                    data = []
                    for row in range(start_row, end_row + 1):
                        row_data = []
                        for col in range(ord(start_col) - ord('A') + 1, ord(end_col) - ord('A') + 2):
                            cell_value = ws[f"{get_column_letter(col)}{row}"].value
                            if cell_value is not None:
                                row_data.append(cell_value)
                        if row_data:
                            data.extend(row_data)
                    
                    # Basic analysis
                    if data:
                        numeric_data = [x for x in data if isinstance(x, (int, float))]
                        if numeric_data:
                            avg = sum(numeric_data) / len(numeric_data)
                            max_val = max(numeric_data)
                            min_val = min(numeric_data)
                            count = len(data)
                            
                            analysis = f"Range {range_to_analyze} contains {count} values. "
                            analysis += f"Average: {avg:.2f}, Max: {max_val}, Min: {min_val}"
                        else:
                            analysis = f"Range {range_to_analyze} contains {len(data)} text values"
                    else:
                        analysis = f"Range {range_to_analyze} is empty"
                    
                    wb.close()
                    print(f"✅ Data analysis completed: {analysis}")
                    return analysis
                    
                except Exception as e:
                    print(f"Openpyxl analysis failed: {e}")
            
            return f"Could not analyze data in range {range_to_analyze}"
            
        except Exception as e:
            print(f"❌ Error analyzing data: {e}")
            return f"Error analyzing data: {str(e)}"
    
    def execute_command(self, command: str) -> str:
        """
        Execute Excel commands based on natural language input
        """
        try:
            command_lower = command.lower()
            print(f"🎯 Executing Excel command: {command}")
            
            # Parse common Excel commands
            if "open" in command_lower and ("file" in command_lower or ".xlsx" in command_lower or ".xls" in command_lower):
                # Extract file path
                file_match = re.search(r'([a-zA-Z]:\\[^\s]+\.xlsx?|[^\s]+\.xlsx?)', command)
                if file_match:
                    file_path = file_match.group(1)
                    return self.open_excel_file(file_path)
                else:
                    return "Please specify the Excel file path"
            
            elif "new" in command_lower and ("workbook" in command_lower or "file" in command_lower):
                return self.create_new_workbook()
            
            elif "go to" in command_lower or "navigate" in command_lower:
                # Extract cell reference
                cell_match = re.search(r'([A-Z]+\d+)', command)
                if cell_match:
                    cell_ref = cell_match.group(1)
                    return self.navigate_to_cell(cell_ref)
                else:
                    return "Please specify a cell reference (e.g., A1, B5)"
            
            elif "enter" in command_lower or "type" in command_lower or "write" in command_lower:
                # Extract cell and data
                cell_match = re.search(r'([A-Z]+\d+)', command)
                if cell_match:
                    cell_ref = cell_match.group(1)
                    # Extract the data to enter
                    data_start = command.find("enter") + 5 if "enter" in command else command.find("type") + 4
                    data = command[data_start:].strip()
                    if cell_match.start() > data_start:
                        data = data[:data.find(cell_match.group(1))].strip()
                    return self.enter_data_in_cell(cell_ref, data)
                else:
                    return "Please specify a cell reference and data to enter"
            
            elif "read" in command_lower or "get" in command_lower:
                # Extract cell reference
                cell_match = re.search(r'([A-Z]+\d+)', command)
                if cell_match:
                    cell_ref = cell_match.group(1)
                    return self.read_cell_data(cell_ref)
                else:
                    return "Please specify a cell reference to read"
            
            elif "format" in command_lower or "style" in command_lower:
                # Extract cell reference and format type
                cell_match = re.search(r'([A-Z]+\d+)', command)
                if cell_match:
                    cell_ref = cell_match.group(1)
                    format_type = "bold"  # Default
                    if "bold" in command_lower:
                        format_type = "bold"
                    elif "italic" in command_lower:
                        format_type = "italic"
                    elif "underline" in command_lower:
                        format_type = "underline"
                    elif "color" in command_lower:
                        format_type = "color"
                    elif "size" in command_lower:
                        format_type = "font_size"
                    elif "center" in command_lower or "align" in command_lower:
                        format_type = "alignment"
                    
                    return self.format_cell(cell_ref, format_type)
                else:
                    return "Please specify a cell reference to format"
            
            elif "formula" in command_lower or "=" in command_lower:
                # Extract cell reference and formula
                cell_match = re.search(r'([A-Z]+\d+)', command)
                if cell_match:
                    cell_ref = cell_match.group(1)
                    # Extract formula (look for = followed by the formula)
                    formula_match = re.search(r'=([^,\s]+)', command)
                    if formula_match:
                        formula = "=" + formula_match.group(1)
                        return self.insert_formula(cell_ref, formula)
                    else:
                        return "Please specify a formula to insert"
                else:
                    return "Please specify a cell reference for the formula"
            
            elif "chart" in command_lower or "graph" in command_lower:
                # Extract chart type and range
                chart_types = ["line", "bar", "pie", "column", "scatter"]
                chart_type = "column"  # Default
                for ct in chart_types:
                    if ct in command_lower:
                        chart_type = ct
                        break
                
                range_match = re.search(r'([A-Z]+\d+:[A-Z]+\d+)', command)
                if range_match:
                    data_range = range_match.group(1)
                    return self.create_chart(chart_type, data_range)
                else:
                    return "Please specify a data range for the chart"
            
            elif "sort" in command_lower:
                # Extract range and sort criteria
                range_match = re.search(r'([A-Z]+\d+:[A-Z]+\d+)', command)
                if range_match:
                    data_range = range_match.group(1)
                    order = "ascending"
                    if "descending" in command_lower or "desc" in command_lower:
                        order = "descending"
                    return self.sort_data(data_range, "A", order)
                else:
                    return "Please specify a range to sort"
            
            elif "filter" in command_lower:
                # Extract range
                range_match = re.search(r'([A-Z]+\d+:[A-Z]+\d+)', command)
                if range_match:
                    data_range = range_match.group(1)
                    return self.filter_data(data_range, "default")
                else:
                    return "Please specify a range to filter"
            
            elif "save" in command_lower:
                return self.save_workbook()
            
            elif "close" in command_lower:
                return self.close_workbook()
            
            elif "sheet" in command_lower or "worksheet" in command_lower:
                # Extract sheet name
                sheet_match = re.search(r'sheet\s+([^\s]+)', command_lower)
                if sheet_match:
                    sheet_name = sheet_match.group(1)
                    return self.switch_worksheet(sheet_name)
                else:
                    return "Please specify a worksheet name"
            
            elif "analyze" in command_lower or "analysis" in command_lower:
                # Extract range
                range_match = re.search(r'([A-Z]+\d+:[A-Z]+\d+)', command)
                if range_match:
                    data_range = range_match.group(1)
                    return self.analyze_data(data_range)
                else:
                    return "Please specify a range to analyze"
            
            else:
                return f"Unknown Excel command: {command}. Try: open file, new workbook, go to A1, enter data, read A1, format cell, create chart, sort data, save, close"
            
        except Exception as e:
            print(f"❌ Error executing Excel command: {e}")
            return f"Error executing Excel command: {str(e)}"

# Global instance for easy access
excel_automation = ExcelAutomation()

def handle_excel_request(query: str) -> str:
    """
    Main function to handle Excel automation requests
    """
    try:
        print(f"📊 Excel Automation Request: {query}")
        
        # Check if it's an Excel-related request
        excel_keywords = [
            "excel", "spreadsheet", "workbook", "worksheet", "cell", "formula",
            "chart", "graph", "sort", "filter", "format", "data", "analysis"
        ]
        
        if any(keyword in query.lower() for keyword in excel_keywords):
            return excel_automation.execute_command(query)
        else:
            return "This doesn't appear to be an Excel-related request. Please specify what you'd like to do with Excel."
            
    except Exception as e:
        print(f"❌ Error in Excel automation: {e}")
        return f"Error in Excel automation: {str(e)}"

# Example usage functions
def open_excel_file(file_path: str) -> str:
    """Open an Excel file"""
    return excel_automation.open_excel_file(file_path)

def create_new_excel_workbook() -> str:
    """Create a new Excel workbook"""
    return excel_automation.create_new_workbook()

def navigate_excel_cell(cell_reference: str) -> str:
    """Navigate to a specific cell"""
    return excel_automation.navigate_to_cell(cell_reference)

def enter_excel_data(cell_reference: str, data: str) -> str:
    """Enter data in a cell"""
    return excel_automation.enter_data_in_cell(cell_reference, data)

def read_excel_data(cell_reference: str) -> str:
    """Read data from a cell"""
    return excel_automation.read_cell_data(cell_reference)

def create_excel_chart(chart_type: str, data_range: str) -> str:
    """Create a chart"""
    return excel_automation.create_chart(chart_type, data_range)

def save_excel_workbook() -> str:
    """Save the workbook"""
    return excel_automation.save_workbook()

def close_excel_workbook() -> str:
    """Close the workbook"""
    return excel_automation.close_workbook()

if __name__ == "__main__":
    # Test the Excel automation
    print("🧪 Testing Excel Automation...")
    
    # Test commands
    test_commands = [
        "create new workbook",
        "go to A1",
        "enter Hello World in A1",
        "read A1",
        "format A1 as bold",
        "go to B1",
        "enter formula =SUM(A1:A10) in B1"
    ]
    
    for command in test_commands:
        print(f"\n🎯 Testing: {command}")
        result = handle_excel_request(command)
        print(f"✅ Result: {result}")
        time.sleep(1)
