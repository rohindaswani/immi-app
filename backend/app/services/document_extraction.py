import os
import re
import io
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, date
from PIL import Image
import pytesseract
import PyPDF2
import pdf2image
import cv2
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedData:
    """Container for extracted document data"""
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    passport_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    place_of_issue: Optional[str] = None
    gender: Optional[str] = None
    
    # Visa specific fields
    visa_type: Optional[str] = None
    visa_class: Optional[str] = None
    control_number: Optional[str] = None
    entries: Optional[str] = None  # Single/Multiple
    annotation: Optional[str] = None
    
    # I-94 specific fields
    i94_number: Optional[str] = None
    admission_date: Optional[date] = None
    admit_until_date: Optional[date] = None
    class_of_admission: Optional[str] = None
    
    # I-797 specific fields
    receipt_number: Optional[str] = None
    priority_date: Optional[date] = None
    notice_type: Optional[str] = None
    validity_from: Optional[date] = None
    validity_to: Optional[date] = None
    beneficiary_name: Optional[str] = None
    petitioner_name: Optional[str] = None
    
    # EAD specific fields
    uscis_number: Optional[str] = None
    category: Optional[str] = None
    card_number: Optional[str] = None
    
    # Additional metadata
    confidence_scores: Dict[str, float] = None
    extracted_text: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.warnings is None:
            self.warnings = []


class DocumentExtractionService:
    """Service for extracting data from immigration documents"""
    
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        
        # Document patterns
        self.patterns = self._initialize_patterns()
        
        # Document type detection keywords with priorities (higher score = more specific)
        self.document_keywords = {
            'passport': {
                'high_priority': ['passport number', 'united states of america passport', 'passport type'],
                'medium_priority': ['passport', 'passeport', 'pasaporte'],
                'patterns': [r'passport\s+no[:\.\s]', r'nationality[:\s]+[A-Z]{2,3}']
            },
            'visa': {
                'high_priority': ['nonimmigrant visa', 'immigrant visa', 'visa type', 'foil number'],
                'medium_priority': ['visa', 'entry', 'control number'],
                'patterns': [r'visa\s+type[:\s]', r'[A-Z]-?[0-9]{1,2}[A-Z]?\s+visa', r'control\s+no[:\s]']
            },
            'i94': {
                'high_priority': ['i-94', 'arrival/departure record', 'admission number', 'cbp.gov'],
                'medium_priority': ['i94', 'admitted until', 'class of admission'],
                'patterns': [r'i-?94\s+number', r'admit\s+until', r'class\s+of\s+admission']
            },
            'i797': {
                'high_priority': ['notice of action', 'i-797', 'uscis', 'receipt number'],
                'medium_priority': ['i797', 'approval notice', 'petition'],
                'patterns': [r'[A-Z]{3}[0-9]{10}', r'receipt\s+number', r'notice\s+type']
            },
            'ead': {
                'high_priority': ['employment authorization document', 'work permit', 'uscis#'],
                'medium_priority': ['ead', 'employment authorization', 'work authorization'],
                'patterns': [r'uscis\s*#?[:\s]', r'category[:\s]+[AC][0-9]{2}', r'card\s+expires']
            },
            'drivers_license': {
                'high_priority': ['driver license', 'drivers license', 'motor vehicle'],
                'medium_priority': ['driving license', 'dl no', 'license number'],
                'patterns': [r'dl\s+no[:\s]', r'license\s+number', r'motor\s+vehicle']
            },
            'green_card': {
                'high_priority': ['permanent resident card', 'green card', 'lawful permanent resident'],
                'medium_priority': ['resident alien', 'permanent resident'],
                'patterns': [r'resident\s+alien', r'permanent\s+resident', r'card\s+expires']
            }
        }
    
    async def extract_from_file(
        self, 
        file_content: bytes, 
        file_type: str,
        document_type_hint: Optional[str] = None
    ) -> ExtractedData:
        """Extract data from a document file"""
        try:
            # Determine file format
            if file_type.lower() in ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff']:
                return await self._extract_from_image(file_content, document_type_hint)
            elif file_type.lower() == 'application/pdf':
                return await self._extract_from_pdf(file_content, document_type_hint)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error extracting document data: {str(e)}")
            result = ExtractedData()
            result.warnings.append(f"Extraction error: {str(e)}")
            return result
    
    async def _extract_from_image(
        self, 
        image_bytes: bytes, 
        document_type_hint: Optional[str] = None
    ) -> ExtractedData:
        """Extract data from an image"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Preprocess image for better OCR
        processed_image = self._preprocess_image(image)
        
        # Extract text using OCR
        text = pytesseract.image_to_string(processed_image)
        
        # Also get detailed OCR data for confidence scores
        ocr_data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
        
        # Detect document type if not provided
        if not document_type_hint:
            document_type_hint = self._detect_document_type(text)
        
        # Extract structured data based on document type
        result = self._extract_structured_data(text, document_type_hint, ocr_data)
        result.extracted_text = text
        
        return result
    
    async def _extract_from_pdf(
        self, 
        pdf_bytes: bytes, 
        document_type_hint: Optional[str] = None
    ) -> ExtractedData:
        """Extract data from a PDF"""
        pdf_file = io.BytesIO(pdf_bytes)
        
        # Try to extract text directly from PDF
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            logger.warning(f"Failed to extract text from PDF: {str(e)}")
        
        # If no text or minimal text, convert to images and OCR
        if len(text.strip()) < 100:
            pdf_file.seek(0)
            images = pdf2image.convert_from_bytes(pdf_bytes)
            
            ocr_texts = []
            for image in images:
                processed_image = self._preprocess_image(image)
                page_text = pytesseract.image_to_string(processed_image)
                ocr_texts.append(page_text)
            
            text = "\n".join(ocr_texts)
        
        # Detect document type if not provided
        if not document_type_hint:
            document_type_hint = self._detect_document_type(text)
        
        # Extract structured data
        result = self._extract_structured_data(text, document_type_hint)
        result.extracted_text = text
        
        return result
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert PIL Image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Deskew if needed
        angle = self._get_skew_angle(denoised)
        if abs(angle) > 0.5:
            denoised = self._rotate_image(denoised, angle)
        
        return denoised
    
    def _get_skew_angle(self, image: np.ndarray) -> float:
        """Detect skew angle in image"""
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = (theta * 180 / np.pi) - 90
                if -45 <= angle <= 45:
                    angles.append(angle)
            
            if angles:
                return np.median(angles)
        
        return 0.0
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle"""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def _detect_document_type(self, text: str) -> Optional[str]:
        """Detect document type from text content with scoring"""
        text_lower = text.lower()
        scores = {}
        
        for doc_type, keyword_data in self.document_keywords.items():
            score = 0
            
            # Check high priority keywords (weight: 10)
            for keyword in keyword_data.get('high_priority', []):
                if keyword in text_lower:
                    score += 10
            
            # Check medium priority keywords (weight: 5)
            for keyword in keyword_data.get('medium_priority', []):
                if keyword in text_lower:
                    score += 5
            
            # Check regex patterns (weight: 15)
            for pattern in keyword_data.get('patterns', []):
                if re.search(pattern, text_lower):
                    score += 15
            
            if score > 0:
                scores[doc_type] = score
        
        # Return document type with highest score
        if scores:
            return max(scores, key=scores.get)
        
        # Fallback: check if it's clearly not an immigration document
        non_immigration_keywords = [
            'blog post', 'article', 'substack', 'newsletter', 'tutorial',
            'engineering', 'team', 'project', 'development', 'software'
        ]
        
        non_immigration_count = sum(1 for keyword in non_immigration_keywords if keyword in text_lower)
        if non_immigration_count >= 3:
            return 'other'  # Not an immigration document
        
        return None
    
    def _extract_structured_data(
        self, 
        text: str, 
        document_type: Optional[str], 
        ocr_data: Optional[Dict] = None
    ) -> ExtractedData:
        """Extract structured data based on document type"""
        result = ExtractedData()
        result.document_type = document_type
        
        if document_type == 'passport':
            return self._extract_passport_data(text, result)
        elif document_type == 'visa':
            return self._extract_visa_data(text, result)
        elif document_type == 'i94':
            return self._extract_i94_data(text, result)
        elif document_type == 'i797':
            return self._extract_i797_data(text, result)
        elif document_type == 'ead':
            return self._extract_ead_data(text, result)
        else:
            # Try generic extraction
            return self._extract_generic_data(text, result)
    
    def _extract_passport_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract data from passport"""
        # Extract passport number
        passport_pattern = r'[A-Z][0-9]{8}|[A-Z]{2}[0-9]{7}'
        passport_match = re.search(passport_pattern, text)
        if passport_match:
            result.passport_number = passport_match.group()
            result.document_number = result.passport_number
        
        # Extract dates
        result.issue_date = self._extract_date(text, ['date of issue', 'issued'])
        result.expiry_date = self._extract_date(text, ['date of expiry', 'expires', 'expiration'])
        result.date_of_birth = self._extract_date(text, ['date of birth', 'dob', 'born'])
        
        # Extract names
        result.full_name = self._extract_name(text)
        if result.full_name:
            parts = result.full_name.split()
            if len(parts) >= 2:
                result.first_name = parts[0]
                result.last_name = ' '.join(parts[1:])
        
        # Extract nationality
        result.nationality = self._extract_field(text, ['nationality', 'citizen'])
        
        # Extract gender
        gender_match = re.search(r'\b(M|F|MALE|FEMALE)\b', text.upper())
        if gender_match:
            result.gender = gender_match.group()[0]
        
        return result
    
    def _extract_visa_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract data from visa"""
        # Extract visa number/control number
        control_pattern = r'[0-9]{8,12}'
        control_match = re.search(f'control[^\n]*{control_pattern}', text, re.IGNORECASE)
        if control_match:
            numbers = re.findall(control_pattern, control_match.group())
            if numbers:
                result.control_number = numbers[0]
                result.document_number = result.control_number
        
        # Extract visa type
        visa_type_pattern = r'[A-Z]-?[0-9]{1,2}[A-Z]?'
        visa_type_match = re.search(f'(?:visa type|class)[^\n]*({visa_type_pattern})', text, re.IGNORECASE)
        if visa_type_match:
            result.visa_type = visa_type_match.group(1)
            result.visa_class = result.visa_type
        
        # Extract dates
        result.issue_date = self._extract_date(text, ['issue date', 'issued'])
        result.expiry_date = self._extract_date(text, ['expiration date', 'expires'])
        
        # Extract entries
        entries_match = re.search(r'(single|multiple|multi)\s*entr', text, re.IGNORECASE)
        if entries_match:
            result.entries = entries_match.group(1).upper()
        
        # Extract name
        result.full_name = self._extract_name(text)
        
        return result
    
    def _extract_i94_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract data from I-94"""
        # Extract I-94 number
        i94_pattern = r'[0-9]{11}'
        i94_match = re.search(f'(?:i-94|admission)[^\n]*({i94_pattern})', text, re.IGNORECASE)
        if i94_match:
            result.i94_number = i94_match.group(1)
            result.document_number = result.i94_number
        
        # Extract admission date
        result.admission_date = self._extract_date(text, ['admission date', 'admitted'])
        
        # Extract admit until date
        result.admit_until_date = self._extract_date(text, ['admit until', 'admitted until'])
        
        # Extract class of admission
        class_pattern = r'[A-Z]-?[0-9]{1,2}[A-Z]?'
        class_match = re.search(f'class of admission[^\n]*({class_pattern})', text, re.IGNORECASE)
        if class_match:
            result.class_of_admission = class_match.group(1)
        
        return result
    
    def _extract_i797_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract data from I-797"""
        # Extract receipt number
        receipt_pattern = r'[A-Z]{3}[0-9]{10}'
        receipt_match = re.search(receipt_pattern, text)
        if receipt_match:
            result.receipt_number = receipt_match.group()
            result.document_number = result.receipt_number
        
        # Extract notice type
        notice_match = re.search(r'notice of (approval|receipt|rejection)', text, re.IGNORECASE)
        if notice_match:
            result.notice_type = notice_match.group(1).upper()
        
        # Extract validity dates
        result.validity_from = self._extract_date(text, ['valid from', 'validity from'])
        result.validity_to = self._extract_date(text, ['valid to', 'validity to', 'valid until'])
        
        # Extract beneficiary name
        beneficiary_match = re.search(r'beneficiary[:\s]+([A-Z\s,]+)', text, re.IGNORECASE)
        if beneficiary_match:
            result.beneficiary_name = beneficiary_match.group(1).strip()
        
        # Extract petitioner name
        petitioner_match = re.search(r'petitioner[:\s]+([A-Z\s,]+)', text, re.IGNORECASE)
        if petitioner_match:
            result.petitioner_name = petitioner_match.group(1).strip()
        
        return result
    
    def _extract_ead_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract data from EAD"""
        # Extract USCIS number
        uscis_pattern = r'[0-9]{3}-[0-9]{3}-[0-9]{3}'
        uscis_match = re.search(uscis_pattern, text)
        if uscis_match:
            result.uscis_number = uscis_match.group()
        
        # Extract card number
        card_pattern = r'[A-Z]{3}[0-9]{10}'
        card_match = re.search(card_pattern, text)
        if card_match:
            result.card_number = card_match.group()
            result.document_number = result.card_number
        
        # Extract category
        category_match = re.search(r'\(([ac]\d{1,2}[a-z]?)\)', text, re.IGNORECASE)
        if category_match:
            result.category = category_match.group(1).upper()
        
        # Extract dates
        result.issue_date = self._extract_date(text, ['card expires', 'valid from'])
        result.expiry_date = self._extract_date(text, ['card expires', 'exp date'])
        
        return result
    
    def _extract_generic_data(self, text: str, result: ExtractedData) -> ExtractedData:
        """Extract generic data when document type is unknown"""
        # Try to extract common fields
        result.full_name = self._extract_name(text)
        result.issue_date = self._extract_date(text, ['issue', 'issued'])
        result.expiry_date = self._extract_date(text, ['expir', 'valid until'])
        
        # Look for any document number patterns
        doc_patterns = [
            r'[A-Z]{3}[0-9]{10}',  # USCIS format
            r'[A-Z][0-9]{8}',      # Passport format
            r'[0-9]{11}',          # I-94 format
        ]
        
        for pattern in doc_patterns:
            match = re.search(pattern, text)
            if match:
                result.document_number = match.group()
                break
        
        return result
    
    def _extract_date(self, text: str, keywords: List[str]) -> Optional[date]:
        """Extract date near keywords"""
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{1,2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{2,4})',  # DD MMM YYYY
            r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2}),?\s+(\d{2,4})',  # MMM DD, YYYY
        ]
        
        for keyword in keywords:
            # Search for date near keyword
            keyword_match = re.search(f'{keyword}[^\n]*', text, re.IGNORECASE)
            if keyword_match:
                search_text = keyword_match.group()
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, search_text, re.IGNORECASE)
                    if date_match:
                        try:
                            return self._parse_date_match(date_match)
                        except:
                            continue
        
        return None
    
    def _parse_date_match(self, match) -> date:
        """Parse date from regex match"""
        groups = match.groups()
        
        if len(groups) == 3:
            if groups[0].isdigit():
                # Numeric date format
                month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                if year < 100:
                    year += 2000 if year < 30 else 1900
                return date(year, month, day)
            else:
                # Month name format
                months = {
                    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                }
                if groups[1].isdigit():
                    # MMM DD YYYY
                    month = months.get(groups[0].upper(), 1)
                    day = int(groups[1])
                    year = int(groups[2])
                else:
                    # DD MMM YYYY
                    day = int(groups[0])
                    month = months.get(groups[1].upper(), 1)
                    year = int(groups[2])
                
                if year < 100:
                    year += 2000 if year < 30 else 1900
                
                return date(year, month, day)
        
        raise ValueError("Could not parse date")
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name from text"""
        # Look for name patterns
        name_keywords = ['name', 'surname', 'given name', 'family name']
        
        for keyword in name_keywords:
            name_match = re.search(f'{keyword}[:\s]+([A-Z][A-Z\s]+)', text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                if len(name) > 3 and len(name) < 100:
                    return name
        
        return None
    
    def _extract_field(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract field value near keywords"""
        for keyword in keywords:
            match = re.search(f'{keyword}[:\s]+([A-Z][A-Z\s]+)', text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = re.sub(r'\s+', ' ', value)
                if len(value) > 2 and len(value) < 100:
                    return value
        
        return None
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for various fields"""
        return {
            'passport_number': re.compile(r'[A-Z][0-9]{8}|[A-Z]{2}[0-9]{7}'),
            'visa_number': re.compile(r'[0-9]{8,12}'),
            'i94_number': re.compile(r'[0-9]{11}'),
            'receipt_number': re.compile(r'[A-Z]{3}[0-9]{10}'),
            'uscis_number': re.compile(r'[0-9]{3}-[0-9]{3}-[0-9]{3}'),
            'date': re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'),
            'visa_type': re.compile(r'[A-Z]-?[0-9]{1,2}[A-Z]?'),
        }