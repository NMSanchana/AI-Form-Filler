import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from PyPDF2 import PdfReader
from models import ExtractedData
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractionConfidence:
    """Track confidence scores for extracted fields"""
    name: float = 0.0
    address: float = 0.0
    phone: float = 0.0
    pincode: float = 0.0
    document_type: str = "unknown"

class UniversalIDExtractor:
    """Universal Indian Government ID Extractor - Works for ALL document types"""
    
    def __init__(self):
        self.common_keywords = {
            'government', 'india', 'unique', 'identification', 'authority',
            'aadhaar', 'enrolment', 'enrollment', 'male', 'female',
            'date', 'birth', 'dob', 'address', 'income', 'tax', 'department',
            'transport', 'license', 'driving', 'vehicle', 'issued', 'valid'
        }
        
        # Document type patterns for intelligent extraction
        self.doc_patterns = {
            'aadhaar': [
                r'(?i)aadhaar',
                r'(?i)unique\s+identification',
                r'(?i)UIDAI',
                r'\d{4}\s?\d{4}\s?\d{4}',
                r'\d{4}/\d{5}/\d{5}'
            ],
            'pan': [
                r'(?i)permanent\s+account',
                r'(?i)income\s+tax',
                r'(?i)PAN',
                r'\b[A-Z]{5}\d{4}[A-Z]\b'
            ],
            'driving_license': [
                r'(?i)driving\s+licence',
                r'(?i)motor\s+vehicle',
                r'(?i)transport',
                r'(?i)authorization\s+to\s+drive',
                r'DL\s*(?:No|Number)',
                r'\b[A-Z]{2}\d{2}\s?\d{11}\b'
            ],
            'voter_id': [
                r'(?i)election\s+commission',
                r'(?i)voter',
                r'(?i)EPIC',
                r'Elector\s*(?:\'s)?\s*Photo',
                r'\b[A-Z]{3}\d{7}\b'
            ],
            'passport': [
                r'(?i)passport',
                r'(?i)republic\s+of\s+india',
                r'(?i)ministry\s+of\s+external',
                r'\b[A-Z]\d{7}\b'
            ]
        }

    def detect_document_type(self, text: str) -> str:
        """Intelligently detect document type"""
        text_upper = text.upper()
        
        scores = {}
        for doc_type, patterns in self.doc_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            scores[doc_type] = score
        
        if scores:
            best_type = max(scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                logger.info(f"🎯 DETECTED DOCUMENT TYPE: {best_type[0].upper()} (confidence: {best_type[1]})")
                return best_type[0]
        
        logger.warning("⚠️  Could not detect document type, using universal extraction")
        return "unknown"

    def preprocess_image_ultimate(self, image_path: str) -> List[Image.Image]:
        """Ultimate preprocessing - optimized for ALL Indian ID documents"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return [Image.open(image_path)]
            
            results = []
            
            # Original
            results.append(Image.open(image_path))
            
            # High resolution if small
            h, w = img.shape[:2]
            if w < 1000 or h < 1000:
                scale = 2.0
                img_large = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                results.append(Image.fromarray(cv2.cvtColor(img_large, cv2.COLOR_BGR2RGB)))
            
            # RGB enhancement
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results.append(Image.fromarray(rgb))
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Super high contrast
            for alpha in [1.5, 2.0, 2.5]:
                enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)
                results.append(Image.fromarray(enhanced))
            
            # Otsu thresholding
            _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results.append(Image.fromarray(thresh_otsu))
            
            # Multiple binary thresholds
            for thresh_val in [100, 127, 150, 180]:
                _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                results.append(Image.fromarray(thresh))
            
            # Inverted
            _, thresh_inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            results.append(Image.fromarray(thresh_inv))
            
            # Adaptive thresholding
            for block_size in [11, 15, 21, 31, 41]:
                try:
                    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                    cv2.THRESH_BINARY, block_size, 2)
                    results.append(Image.fromarray(adaptive))
                except:
                    pass
            
            # CLAHE enhancement
            for clip in [2.0, 3.0, 4.0]:
                clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
                clahe_img = clahe.apply(gray)
                results.append(Image.fromarray(clahe_img))
                
                _, clahe_thresh = cv2.threshold(clahe_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                results.append(Image.fromarray(clahe_thresh))
            
            # Denoising
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            results.append(Image.fromarray(denoised))
            _, denoised_thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results.append(Image.fromarray(denoised_thresh))
            
            # Bilateral filter
            bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
            results.append(Image.fromarray(bilateral))
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph_close = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            results.append(Image.fromarray(morph_close))
            
            # Erosion and dilation
            eroded = cv2.erode(gray, kernel, iterations=1)
            results.append(Image.fromarray(eroded))
            
            dilated = cv2.dilate(gray, kernel, iterations=1)
            results.append(Image.fromarray(dilated))
            
            # Sharpening
            kernel_sharp = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(gray, -1, kernel_sharp)
            results.append(Image.fromarray(sharpened))
            
            # Gaussian blur + threshold
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, blur_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            results.append(Image.fromarray(blur_thresh))
            
            logger.info(f"✨ Generated {len(results)} preprocessed versions")
            return results
            
        except Exception as e:
            logger.error(f"❌ Preprocessing error: {str(e)}")
            try:
                return [Image.open(image_path)]
            except:
                return []

    def extract_text_maximum_coverage(self, file_path: str) -> str:
        """Maximum OCR coverage - tries EVERYTHING"""
        try:
            all_texts = []
            processed_images = self.preprocess_image_ultimate(file_path)
            
            psm_modes = [3, 4, 6, 11, 12]
            oem_modes = [1, 2, 3]
            
            logger.info(f"🔍 Running OCR: {len(processed_images)} images × {len(psm_modes)} PSM × {len(oem_modes)} OEM = {len(processed_images) * len(psm_modes) * len(oem_modes)} attempts")
            
            attempt = 0
            for img_idx, img in enumerate(processed_images):
                for oem in oem_modes:
                    for psm in psm_modes:
                        try:
                            config = f'--oem {oem} --psm {psm}'
                            text = pytesseract.image_to_string(img, config=config, lang='eng')
                            if text and len(text.strip()) > 10:
                                all_texts.append(f"[V{img_idx}_OEM{oem}_PSM{psm}]\n{text}\n")
                                attempt += 1
                        except:
                            continue
            
            logger.info(f"✅ Successfully extracted {attempt} text versions")
            combined = "\n===SPLIT===\n".join(all_texts)
            return combined
            
        except Exception as e:
            logger.error(f"❌ OCR error: {str(e)}")
            return ""

    def clean_text_smart(self, text: str) -> str:
        """Smart text cleaning for government documents"""
        replacements = {
            '|': 'I', '!': 'I', 
            '§': 'S', '€': 'E', '©': 'C', '®': 'R',
            '@': 'a', '$': 'S', 
            '  ': ' ', '   ': ' ', '\t': ' '
        }
        
        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned

    def extract_name_universal(self, text: str, doc_type: str) -> Tuple[str, float]:
        """Universal name extraction - works for ALL document types"""
        text = self.clean_text_smart(text)
        found_names = {}
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Document-specific patterns
        if doc_type == 'pan':
            patterns = [
                (r'(?:Name|NAME)\s*[:\n]\s*([A-Z][A-Za-z\s]{3,50}?)(?=\n|Date of Birth|Father)', 0.98),
                (r'(?:Name|NAME)\s+([A-Z][A-Z\s]{3,50}?)(?=\n|\s{2,})', 0.95),
            ]
        elif doc_type == 'driving_license':
            patterns = [
                (r'(?:Name|NAME|Holder)[:\s]+([A-Z][A-Za-z\s]{3,50}?)(?=\n|S/O|D/O|DOB|Address)', 0.98),
                (r'(?:Name|NAME)\s*[:\n]\s*([A-Z][A-Za-z\s]{3,50}?)(?=\n)', 0.95),
            ]
        elif doc_type == 'aadhaar':
            patterns = [
                (r'To[\s\n:]+([A-Z][a-z]{2,15}(?:\s+[A-Z](?:\s+[A-Z])?)?(?:\s+[A-Z][a-z]{2,15})?)', 0.98),
                (r'\b([A-Z][a-z]{3,15}\s+[A-Z]\s+[A-Z])\b', 0.95),
            ]
        else:
            patterns = [
                (r'(?:Name|NAME|To|TO)[:\s\n]+([A-Z][A-Za-z\s]{3,50}?)(?=\n|S/O|D/O|Father|Mother|DOB|Address|\d)', 0.95),
            ]
        
        # Add universal patterns
        patterns.extend([
            (r'(?:To|Name|NAME)[:\s]+([A-Z][A-Za-z\s]{3,50}?)(?=\n|$|[,.]|\s+(?:S/O|D/O|Father))', 0.92),
            (r'\b([A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15}){1,3})\b', 0.80),
            (r'\b([A-Z][a-z]{3,15}\s+[A-Z](?:\s+[A-Z])?)\b', 0.85),
            (r'\b([A-Z]{3,15}(?:\s+[A-Z]{3,15}){1,3})\b', 0.75),
            (r'(?:Card|CARD|License|LICENSE)[\s\n]{1,20}([A-Z][A-Za-z\s]{5,50}?)(?=\n|Father|Address|S/O|D/O)', 0.85),
        ])
        
        # Try all patterns
        for pattern, confidence in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                
                if self.is_valid_name(name):
                    found_names[name] = found_names.get(name, 0) + confidence
        
        # Line-by-line scanning
        for i, line in enumerate(lines):
            if any(kw in line.upper() for kw in ['GOVERNMENT', 'INDIA', 'INCOME TAX', 'DEPARTMENT', 'MINISTRY']):
                continue
            
            if re.match(r'^[A-Z][A-Za-z\s]{5,60}$', line):
                if not any(char.isdigit() for char in line):
                    if self.is_valid_name(line):
                        found_names[line] = found_names.get(line, 0) + 0.70
        
        # Sort by confidence
        if found_names:
            sorted_names = sorted(found_names.items(), key=lambda x: x[1], reverse=True)
            best_name = sorted_names[0]
            logger.info(f"✅ NAME FOUND: '{best_name[0]}' (confidence: {best_name[1]:.2f})")
            logger.info(f"   Other candidates: {[n[0] for n in sorted_names[1:3]]}")
            return best_name
        
        logger.warning("❌ NAME NOT FOUND!")
        return "", 0.0

    def is_valid_name(self, name: str) -> bool:
        """Strict name validation for Indian names"""
        if not name or len(name) < 3 or len(name) > 70:
            return False
        
        name = re.sub(r'\s+', ' ', name).strip()
        parts = name.split()
        
        if len(parts) < 1 or len(parts) > 5:
            return False
        
        for part in parts:
            if not re.match(r'^[A-Za-z.]+$', part):
                return False
        
        name_lower = name.lower()
        exclude_words = [
            'government', 'india', 'unique', 'identification', 'authority',
            'aadhaar', 'income tax', 'department', 'permanent', 'account',
            'driving', 'license', 'motor', 'vehicle', 'transport',
            'date of birth', 'father', 'address', 'signature'
        ]
        
        if any(word in name_lower for word in exclude_words):
            return False
        
        if not name[0].isupper():
            return False
        
        return True

    def extract_address_universal(self, text: str, doc_type: str) -> Tuple[str, float]:
        """Universal address extraction for all documents"""
        
        if doc_type == 'pan':
            patterns = [
                (r'(?:Address|ADDRESS)[:\s]+((?:.*?(?:\n.*?){1,5}?)?\d{6})', 0.95),
                (r'(?:Flat|House|Plot|Door)[^\n]*(?:\n[^\n]+){1,4}\d{6}', 0.90),
            ]
        elif doc_type == 'driving_license':
            patterns = [
                (r'(?:Address|ADDRESS)[:\s]+((?:.*?(?:\n.*?){1,6}?)?\d{6})', 0.95),
                (r'(?:House|Door|Flat|No)[^\n]*(?:\n[^\n]+){1,5}\d{6}', 0.90),
            ]
        else:
            patterns = [
                (r'((?:NO|No|D\.?No|H\.?No)[:\s]*\d+[/\-,]?\d*[^\n]*?(?:NAGAR|Nagar|POST|Post|Road|ROAD|Street|STREET|Patti|Village|Dist|District)[^\n]*?\d{6})', 0.98),
                (r'((?:NO|No|D\.?No)[:\s]*\d+[/\-]?\d*[^\n]*(?:\n[^\n]+){1,6}?\d{6})', 0.95),
            ]
        
        patterns.extend([
            (r'(?:Address|ADDRESS)[:\s]+(.*?\d{6})', 0.88),
            (r'([^\n]*(?:Nagar|Post|Road|Street|District|Dist|Village|City)[^\n]*\d{6})', 0.80),
        ])
        
        for pattern, confidence in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                addr = match.group(1)
                addr = re.sub(r'\s+', ' ', addr)
                addr = re.sub(r'\n+', ', ', addr)
                addr = addr.strip()
                
                if len(addr) > 20 and not any(kw in addr.upper() for kw in ['GOVERNMENT', 'INCOME TAX']):
                    logger.info(f"✅ ADDRESS FOUND: {addr[:60]}... (confidence: {confidence})")
                    return addr, confidence
        
        # Fallback
        lines = text.split('\n')
        address_parts = []
        capturing = False
        
        for line in lines:
            line = line.strip()
            
            if re.search(r'(?:Address|ADDRESS|NO|No|D\.?No|House|Flat)', line, re.IGNORECASE):
                if not any(kw in line.upper() for kw in ['GOVERNMENT', 'DEPARTMENT', 'INCOME TAX']):
                    capturing = True
            
            if capturing and line:
                if any(kw in line.upper() for kw in ['GOVERNMENT', 'INDIA', 'INCOME TAX', 'DEPARTMENT', 'SIGNATURE']):
                    continue
                
                address_parts.append(line)
                
                if re.search(r'\d{6}', line):
                    break
                
                if len(address_parts) > 10:
                    break
        
        if address_parts:
            full_addr = ' '.join(address_parts)
            full_addr = re.sub(r'\s+', ' ', full_addr)
            if len(full_addr) > 20:
                logger.info(f"✅ ADDRESS ASSEMBLED: {full_addr[:60]}...")
                return full_addr, 0.70
        
        logger.warning("❌ ADDRESS NOT FOUND!")
        return "", 0.0

    def extract_all_ids_comprehensive(self, text: str) -> Dict[str, str]:
        """Comprehensive ID extraction for ALL document types"""
        ids = {}
        
        # AADHAAR
        aadhaar_patterns = [
            r'\b(\d{4}\s?\d{4}\s?\d{4})\b',
            r'(?:Aadhaar|AADHAAR|UID)[:\s]*(\d{4}\s?\d{4}\s?\d{4})',
        ]
        for pattern in aadhaar_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                aadhaar = re.sub(r'[^\d]', '', match)
                if len(aadhaar) == 12 and aadhaar.isdigit():
                    if not aadhaar.startswith(('6','7','8','9')):
                        ids['aadhaar'] = aadhaar
                        break
        
        # ENROLLMENT
        enrol_pattern = r'(\d{4}[/]\d{5}[/]\d{5})'
        match = re.search(enrol_pattern, text)
        if match:
            ids['enrollment'] = match.group(1)
        
        # PAN
        pan_patterns = [
            r'\b([A-Z]{5}\d{4}[A-Z])\b',
            r'(?:PAN|Permanent Account)[^\n]*\n\s*([A-Z]{5}\d{4}[A-Z])',
        ]
        for pattern in pan_patterns:
            match = re.search(pattern, text)
            if match:
                pan = match.group(1)
                if re.match(r'^[A-Z]{3}[ABCFGHLJPTF][A-Z]\d{4}[A-Z]$', pan):
                    ids['pan'] = pan
                    break
        
        # DRIVING LICENSE
        dl_patterns = [
            r'\b([A-Z]{2}[-\s]?\d{2}[-\s]?\d{11})\b',
            r'\b([A-Z]{2}\d{13,14})\b',
            r'(?:DL|License|Licence)\s*(?:No|Number|#)?[:\s]*([A-Z]{2}[-\s]?\d{13,15})',
        ]
        for pattern in dl_patterns:
            match = re.search(pattern, text)
            if match:
                dl = match.group(1).replace(' ', '').replace('-', '')
                if len(dl) >= 13 and dl[:2].isalpha():
                    ids['driving_license'] = match.group(1)
                    break
        
        # VOTER ID
        voter_patterns = [
            r'\b([A-Z]{3}\d{7})\b',
            r'(?:EPIC|Elector|Voter)[^\n]*\n\s*([A-Z]{3}\d{7})',
        ]
        for pattern in voter_patterns:
            match = re.search(pattern, text)
            if match:
                voter_id = match.group(1)
                if not any(word in voter_id for word in ['PAN', 'TAX']):
                    ids['voter_id'] = voter_id
                    break
        
        # PASSPORT
        passport_patterns = [
            r'\b([A-Z]\d{7})\b',
            r'(?:Passport|Pass Port)[^\n]*\n\s*([A-Z]\d{7})',
        ]
        for pattern in passport_patterns:
            match = re.search(pattern, text)
            if match:
                ids['passport'] = match.group(1)
                break
        
        if ids:
            logger.info(f"✅ IDs FOUND: {list(ids.keys())}")
            for id_type, id_value in ids.items():
                logger.info(f"   {id_type.upper()}: {id_value}")
        else:
            logger.warning("❌ NO ID NUMBERS FOUND!")
        
        return ids

    def extract_father_name(self, text: str) -> Tuple[str, float]:
        """Extract father's name"""
        patterns = [
            (r'(?:S/O|s/o|Son of|SON OF)[:\s]+([A-Z][A-Za-z\s]{3,40}?)(?=\n|,|Address|DOB|\d)', 0.95),
            (r'(?:D/O|d/o|Daughter of|DAUGHTER OF)[:\s]+([A-Z][A-Za-z\s]{3,40}?)(?=\n|,|Address|DOB|\d)', 0.95),
            (r'(?:Father|FATHER)[:\s\']+s?\s*(?:Name)?[:\s]*([A-Z][A-Za-z\s]{3,40}?)(?=\n|,|Mother)', 0.90),
        ]
        
        for pattern, confidence in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                father = match.group(1).strip()
                father = re.sub(r'\s+', ' ', father)
                if self.is_valid_name(father):
                    logger.info(f"✅ FATHER'S NAME: {father}")
                    return father, confidence
        
        return "", 0.0

    def extract_phone_universal(self, text: str) -> List[str]:
        """Universal phone extraction"""
        phones = []
        
        patterns = [
            r'(?:Phone|Mobile|Mob|Contact|Tel|Cell)[:\s]*([6-9]\d{9})',
            r'\+91[\s-]?([6-9]\d{9})',
            r'\b([6-9]\d{9})\b',
            r'(\d{5}[\s-]?\d{5})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                phone = re.sub(r'[^\d]', '', match)
                if len(phone) == 10 and phone[0] in '6789':
                    if len(set(phone)) > 3:
                        if phone not in phones:
                            phones.append(phone)
        
        if phones:
            logger.info(f"✅ PHONE(S) FOUND: {phones}")
        return phones

    def extract_complete_data(self, text: str) -> ExtractedData:
        """UNIVERSAL extraction - works for ALL Indian government IDs"""
        data = ExtractedData()
        
        logger.info("="*80)
        logger.info("🚀 STARTING UNIVERSAL ID EXTRACTION")
        logger.info("="*80)
        
        # Detect document type
        doc_type = self.detect_document_type(text)
        
        # Extract based on document type
        data.name, name_conf = self.extract_name_universal(text, doc_type)
        data.address, addr_conf = self.extract_address_universal(text, doc_type)
        
        # Extract ALL ID types
        ids = self.extract_all_ids_comprehensive(text)
        
        # Prioritize based on document type
        if doc_type == 'pan' and 'pan' in ids:
            data.idNumber = ids['pan']
        elif doc_type == 'driving_license' and 'driving_license' in ids:
            data.idNumber = ids['driving_license']
        elif doc_type == 'aadhaar':
            if 'aadhaar' in ids:
                data.idNumber = ids['aadhaar']
            elif 'enrollment' in ids:
                data.idNumber = ids['enrollment']
        elif 'voter_id' in ids:
            data.idNumber = ids['voter_id']
        elif 'passport' in ids:
            data.idNumber = ids['passport']
        else:
            if ids:
                data.idNumber = list(ids.values())[0]
        
        # Extract other fields
        phones = self.extract_phone_universal(text)
        if phones:
            data.phone = phones[0]
        
        # Pincode
        pincode_matches = re.findall(r'\b([1-9]\d{5})\b', text)
        if pincode_matches:
            data.pincode = pincode_matches[0]
            logger.info(f"✅ PINCODE: {data.pincode}")
        
        # Date of Birth
        dob_patterns = [
            r'(?:DOB|Date of Birth|Birth|D\.O\.B)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob = match.group(1).replace('-', '/')
                year = int(dob.split('/')[-1])
                if 1920 <= year <= 2024:
                    data.dateOfBirth = dob
                    logger.info(f"✅ DOB: {dob}")
                    break
        
        # Gender
        if re.search(r'\b(Female|FEMALE|F)\b', text):
            data.gender = 'Female'
            logger.info(f"✅ GENDER: Female")
        elif re.search(r'\b(Male|MALE|M)\b', text):
            data.gender = 'Male'
            logger.info(f"✅ GENDER: Male")
        
        # Email
        email_match = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', text)
        if email_match:
            data.email = email_match.group(1)
            logger.info(f"✅ EMAIL: {data.email}")
        
        # Father's name
        data.fatherName, father_conf = self.extract_father_name(text)
        
        # City
        cities = [
            'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem',
            'Tirunelveli', 'Tiruppur', 'Erode', 'Vellore', 'Thoothukudi',
            'Dindigul', 'Thanjavur', 'Virudhunagar', 'Karur', 'Namakkal',
            'Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Hyderabad', 
            'Pune', 'Kolkata', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow',
            'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Patna',
            'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik',
            'Kochi', 'Thiruvananthapuram', 'Kozhikode', 'Kannur'
        ]
        
        for city in cities:
            if city.lower() in text.lower():
                data.city = city
                logger.info(f"✅ CITY: {city}")
                break
        
        # State
        states = [
            'Tamil Nadu', 'Karnataka', 'Kerala', 'Andhra Pradesh', 
            'Telangana', 'Maharashtra', 'Delhi', 'Gujarat', 'Rajasthan',
            'Uttar Pradesh', 'Madhya Pradesh', 'West Bengal', 'Bihar',
            'Punjab', 'Haryana', 'Odisha', 'Assam', 'Jharkhand',
            'Chhattisgarh', 'Uttarakhand', 'Goa', 'Himachal Pradesh'
        ]
        
        for state in states:
            if state.lower() in text.lower() or state.replace(' ', '').lower() in text.lower():
                data.state = state
                logger.info(f"✅ STATE: {state}")
                break
        
        # Final Summary
        logger.info("="*80)
        logger.info("📋 EXTRACTION SUMMARY:")
        logger.info(f"   Document Type: {doc_type.upper()}")
        logger.info(f"   Name: {data.name or '❌ NOT FOUND'}")
        logger.info(f"   Father: {data.fatherName or '❌ NOT FOUND'}")
        logger.info(f"   DOB: {data.dateOfBirth or '❌ NOT FOUND'}")
        logger.info(f"   Gender: {data.gender or '❌ NOT FOUND'}")
        logger.info(f"   Address: {(data.address[:60] + '...') if data.address else '❌ NOT FOUND'}")
        logger.info(f"   City: {data.city or '❌ NOT FOUND'}")
        logger.info(f"   State: {data.state or '❌ NOT FOUND'}")
        logger.info(f"   Pincode: {data.pincode or '❌ NOT FOUND'}")
        logger.info(f"   Phone: {data.phone or '❌ NOT FOUND'}")
        logger.info(f"   Email: {data.email or '❌ NOT FOUND'}")
        logger.info(f"   ID Number: {data.idNumber or '❌ NOT FOUND'}")
        logger.info("="*80)
        
        return data


# Legacy functions for backward compatibility
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return ""


def extract_text_from_image(file_path: str) -> str:
    """Extract text from image using universal extractor"""
    extractor = UniversalIDExtractor()
    return extractor.extract_text_maximum_coverage(file_path)


def extract_data_from_text(text: str) -> ExtractedData:
    """Extract data using universal extractor"""
    extractor = UniversalIDExtractor()
    return extractor.extract_complete_data(text)


def merge_data(data_list: list) -> ExtractedData:
    """Merge multiple extractions"""
    merged = ExtractedData()
    fields = ['name', 'fatherName', 'dateOfBirth', 'address', 'city', 'state', 
              'pincode', 'phone', 'email', 'idNumber', 'gender']
    
    for field in fields:
        best = ""
        for data in data_list:
            val = getattr(data, field)
            if val and len(str(val).strip()) > len(best):
                best = str(val).strip()
        if best:
            setattr(merged, field, best)
    
    return merged