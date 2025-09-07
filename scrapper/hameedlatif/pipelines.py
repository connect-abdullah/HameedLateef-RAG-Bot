# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
import re


class HameedlatifPipeline:
    def __init__(self):
        self.seen_urls = set()
        self.seen_content = set()

    def clean_text_content(self, text):
        """Clean text content for customer support bot"""
        if not text:
            return ""
        
        # Remove technical junk patterns
        junk_patterns = [
            r'\.css[^}]*\}',  # CSS
            r'jQuery[^;]*;',  # jQuery
            r'function\s*\([^}]*\}',  # JavaScript functions
            r'var\s+[^;]*;',  # JavaScript variables
            r'@media[^}]*\}',  # Media queries
            r'rgba?\([^)]+\)',  # Color values
            r'#[0-9a-fA-F]{3,6}',  # Hex colors
            r'px;?|em;?|rem;?',  # CSS units
            r'background-color[^;]*;',  # CSS properties
            r'border[^;]*;',
            r'padding[^;]*;',
            r'margin[^;]*;',
            r'\{[^}]*\}',  # Any remaining CSS blocks
            r'Skip to content',
            r'Back to top',
            r'window\.',
            r'<!-- [^>]* -->',  # HTML comments
        ]
        
        for pattern in junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def is_meaningful_content(self, text):
        """Check if content is meaningful for customer support - be less strict"""
        if not text or len(text) < 20:  # Reduced from 50 to 20
            return False
        
        # Skip if mostly technical junk - be more lenient
        junk_indicators = ['px', 'rgba', 'function', 'var ', 'jQuery', '.css', 'background-color']
        junk_count = sum(1 for indicator in junk_indicators if indicator in text)
        
        # Be more lenient - allow more junk
        if junk_count > 10:  # Increased from 3 to 10
            return False
        
        return True

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Skip duplicate URLs
        if adapter.get('url') in self.seen_urls:
            spider.logger.info(f"Duplicate URL: {adapter.get('url')}")
            return None
        
        self.seen_urls.add(adapter.get('url'))
        
        # Clean main content - but don't be too strict
        main_content = adapter.get('main_content', '')
        if main_content:
            cleaned_content = self.clean_text_content(main_content)
            # Be less strict - only skip if really no content
            if len(cleaned_content) < 20:
                spider.logger.info(f"Skipping page with very little content: {adapter.get('url')}")
                return None
            adapter['main_content'] = cleaned_content
        else:
            # If no main content, still try to keep the item
            spider.logger.info(f"No main content found for: {adapter.get('url')}")
            adapter['main_content'] = ""
        
        # Don't skip based on content similarity - keep all unique URLs
        
        # Clean other fields
        for field in ['departments', 'services', 'procedures', 'faqs', 'visitor_info', 'doctors']:
            items = adapter.get(field, [])
            if items:
                cleaned_items = []
                for text in items:
                    cleaned = self.clean_text_content(text) if isinstance(text, str) else text
                    if cleaned and len(cleaned) > 3:  # Be less strict
                        cleaned_items.append(cleaned)
                adapter[field] = list(set(cleaned_items))  # Remove duplicates
        
        # Clean contact info
        phone_numbers = adapter.get('phone_numbers', [])
        if phone_numbers:
            # Clean and validate phone numbers
            cleaned_phones = []
            for phone in phone_numbers:
                # Remove non-digit characters except + and spaces
                clean_phone = re.sub(r'[^\d+\s\-\(\)]', '', phone)
                if len(clean_phone) >= 7:  # Minimum phone number length
                    cleaned_phones.append(clean_phone)
            adapter['phone_numbers'] = list(set(cleaned_phones))
        
        # Clean email addresses
        emails = adapter.get('email_addresses', [])
        if emails:
            valid_emails = [email for email in emails if '@' in email and '.' in email]
            adapter['email_addresses'] = list(set(valid_emails))
        
        return item
