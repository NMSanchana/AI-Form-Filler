import os
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from playwright.async_api import async_playwright
from config import OUTPUT_DIR
import asyncio

async def fill_pdf(form_path: str, data: dict) -> str:
    """Fill PDF form with actual data"""
    try:
        reader = PdfReader(form_path)
        writer = PdfWriter()
        
        has_fields = False
        if reader.get_form_text_fields():
            has_fields = True
            
            for page in reader.pages:
                writer.add_page(page)
            
            for page_num in range(len(writer.pages)):
                page = writer.pages[page_num]
                
                if '/Annots' in page:
                    for annot in page['/Annots']:
                        try:
                            field = annot.get_object()
                            if '/T' in field:
                                field_name = str(field['/T']).lower()
                                
                                for key, value in data.items():
                                    if value and (key.lower() in field_name or field_name in key.lower()):
                                        try:
                                            writer.update_page_form_field_values(
                                                page,
                                                {field['/T']: str(value)}
                                            )
                                        except:
                                            pass
                        except:
                            pass
        
        output_filename = f"filled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if has_fields:
            with open(output_path, 'wb') as f:
                writer.write(f)
        else:
            output_path = create_filled_pdf_overlay(data)
        
        return output_path
        
    except Exception as e:
        print(f"PDF filling error: {str(e)}")
        return create_filled_pdf_overlay(data)

def create_filled_pdf_overlay(data: dict) -> str:
    """Create filled PDF with data"""
    output_filename = f"filled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Filled Form Data")
    
    c.setStrokeColorRGB(0.2, 0.2, 0.8)
    c.setLineWidth(2)
    c.line(50, height - 60, width - 50, height - 60)
    
    y = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.2, 0.2, 0.2)
    
    labels = {
        'name': 'Full Name',
        'fatherName': "Father's Name",
        'dateOfBirth': 'Date of Birth',
        'gender': 'Gender',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'pincode': 'Pincode',
        'phone': 'Phone Number',
        'email': 'Email Address',
        'idNumber': 'ID Number'
    }
    
    for key, value in data.items():
        if value and value.strip():
            label = labels.get(key, key.title())
            
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"{label}:")
            
            c.setFont("Helvetica", 11)
            value_text = str(value)[:80]
            c.drawString(220, y, value_text)
            
            y -= 30
            
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 50
    
    c.save()
    return output_path

def find_chrome_path():
    """Find Chrome installation path"""
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Darwin":
        paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    else:
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

async def fill_google_form(page, data: dict) -> tuple:
    """Special handler for Google Forms"""
    print("🎯 Detected Google Form - using special handler\n")
    
    filled_count = 0
    failed_fields = []
    
    # Wait for form to load
    await asyncio.sleep(2)
    
    # Field mappings for Google Forms
    field_mappings = {
        'name': ['name', 'full name', 'your name', 'applicant'],
        'fatherName': ['father', "father's name", 'parent', 'guardian'],
        'dateOfBirth': ['dob', 'date of birth', 'birth', 'birthday'],
        'address': ['address', 'street', 'location'],
        'city': ['city', 'town'],
        'state': ['state', 'province'],
        'pincode': ['pincode', 'pin', 'zip', 'postal'],
        'phone': ['phone', 'mobile', 'contact', 'number'],
        'email': ['email', 'e-mail', 'mail'],
        'idNumber': ['id', 'aadhaar', 'aadhar', 'identification'],
        'gender': ['gender', 'sex']
    }
    
    # Get all form questions
    questions = await page.query_selector_all('[role="listitem"]')
    print(f"📋 Found {len(questions)} questions in the form\n")
    
    for key, value in data.items():
        if not value or not str(value).strip():
            continue
        
        value = str(value).strip()
        print(f"🔍 Trying to fill: {key} = '{value}'")
        
        field_filled = False
        possible_labels = field_mappings.get(key, [key])
        
        # Try to find matching question
        for question in questions:
            try:
                # Get question text
                question_text = await question.inner_text()
                question_text_lower = question_text.lower()
                
                # Check if any possible label matches this question
                matched = False
                for label in possible_labels:
                    if label.lower() in question_text_lower:
                        matched = True
                        break
                
                if not matched:
                    continue
                
                print(f"   ✓ Found question: {question_text[:50]}...")
                
                # Try to find input field within this question
                # Google Forms uses specific input types
                input_selectors = [
                    'input[type="text"]',
                    'input[type="email"]',
                    'input[type="tel"]',
                    'textarea',
                    'input[aria-label]'
                ]
                
                for selector in input_selectors:
                    try:
                        input_field = await question.query_selector(selector)
                        
                        if input_field:
                            # Check if visible
                            is_visible = await input_field.is_visible()
                            if not is_visible:
                                continue
                            
                            # Click and fill
                            await input_field.click()
                            await asyncio.sleep(0.3)
                            
                            # Clear existing content
                            await input_field.fill('')
                            await asyncio.sleep(0.2)
                            
                            # Type value
                            await input_field.type(value, delay=30)
                            
                            # Verify it was filled
                            await asyncio.sleep(0.3)
                            filled_value = await input_field.input_value()
                            
                            if filled_value:
                                print(f"   ✅ Successfully filled with: {value}")
                                filled_count += 1
                                field_filled = True
                                break
                    except:
                        continue
                
                if field_filled:
                    break
                    
            except Exception as e:
                continue
        
        if not field_filled:
            failed_fields.append(key)
            print(f"   ❌ Could not fill: {key}")
    
    return filled_count, failed_fields

async def fill_standard_form(page, data: dict) -> tuple:
    """Handler for standard HTML forms"""
    print("🎯 Standard HTML form detected\n")
    
    filled_count = 0
    failed_fields = []
    
    field_mappings = {
        'name': ['name', 'fullname', 'full_name', 'full-name'],
        'fatherName': ['father', 'father_name', 'fathername'],
        'dateOfBirth': ['dob', 'date_of_birth', 'birthdate'],
        'address': ['address', 'street', 'addr'],
        'city': ['city', 'town'],
        'state': ['state', 'province'],
        'pincode': ['pincode', 'pin', 'zip', 'postal'],
        'phone': ['phone', 'mobile', 'contact', 'tel'],
        'email': ['email', 'mail'],
        'idNumber': ['id', 'aadhaar', 'pan'],
        'gender': ['gender', 'sex']
    }
    
    for key, value in data.items():
        if not value or not str(value).strip():
            continue
        
        value = str(value).strip()
        print(f"🔍 Filling: {key} = '{value}'")
        
        field_filled = False
        possible_names = field_mappings.get(key, [key])
        
        for field_name in possible_names:
            if field_filled:
                break
            
            selectors = [
                f'input[name="{field_name}"]',
                f'input[id="{field_name}"]',
                f'textarea[name="{field_name}"]',
                f'select[name="{field_name}"]',
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    
                    if not element:
                        continue
                    
                    is_visible = await element.is_visible()
                    if not is_visible:
                        continue
                    
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    
                    if tag_name == 'select':
                        try:
                            await element.select_option(value=value)
                            print(f"   ✅ Filled dropdown: {selector}")
                            filled_count += 1
                            field_filled = True
                            break
                        except:
                            pass
                    
                    elif tag_name in ['input', 'textarea']:
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(0.2)
                        await element.click()
                        await asyncio.sleep(0.2)
                        await element.fill(value)
                        
                        print(f"   ✅ Filled: {selector}")
                        filled_count += 1
                        field_filled = True
                        break
                
                except:
                    continue
        
        if not field_filled:
            failed_fields.append(key)
            print(f"   ❌ Not found: {key}")
    
    return filled_count, failed_fields

async def fill_url(url: str, data: dict) -> dict:
    """
    Universal form filler - handles Google Forms and standard HTML forms
    """
    print("\n" + "="*70)
    print("🚀 FORM FILLER STARTING")
    print("="*70)
    
    try:
        chrome_path = find_chrome_path()
        
        if not chrome_path:
            print("❌ Chrome not found!")
            return {
                'success': False,
                'message': 'Chrome browser not found',
                'filled_count': 0
            }
        
        print(f"✅ Chrome: {chrome_path}")
        print(f"📍 URL: {url}\n")
        
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            
            browser = await p.chromium.launch(
                headless=False,
                executable_path=chrome_path,
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            print("📂 Opening page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(3)
            
            print("✅ Page loaded!\n")
            
            # Detect form type
            is_google_form = 'docs.google.com/forms' in url
            
            print("="*70)
            print("FILLING FIELDS")
            print("="*70 + "\n")
            
            # Use appropriate filler
            if is_google_form:
                filled_count, failed_fields = await fill_google_form(page, data)
            else:
                filled_count, failed_fields = await fill_standard_form(page, data)
            
            print("\n" + "="*70)
            print("SUMMARY")
            print("="*70)
            print(f"✅ Filled: {filled_count} fields")
            print(f"❌ Failed: {len(failed_fields)} fields")
            if failed_fields:
                print(f"   Missing: {', '.join(failed_fields)}")
            print("="*70 + "\n")
            
            print("⏳ Browser stays open for 60 seconds")
            print("👉 Review and submit manually\n")
            
            await asyncio.sleep(60)
            
            print("🔚 Closing browser...\n")
            await browser.close()
            
            return {
                'success': True,
                'message': f'Filled {filled_count}/{len(data)} fields',
                'filled_count': filled_count,
                'total_fields': len(data),
                'failed_fields': failed_fields
            }
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'filled_count': 0,
            'failed_fields': []
        }