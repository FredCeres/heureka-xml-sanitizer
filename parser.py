from lxml import etree
import sys
import json

def parse_heureka_xml(xml_path):
    mandatory_tags = ['ITEM_ID', 'PRODUCTNAME', 'DESCRIPTION', 'URL', 'PRICE_VAT', 'DELIVERY_DATE', 'CATEGORYTEXT']
    
    errors = []
    total_items = 0
    
    try:
        # Use iterparse for memory efficiency with large XML files
        context = etree.iterparse(xml_path, events=('end',), tag='SHOPITEM')
        
        for event, elem in context:
            total_items += 1
            item_id = elem.findtext('ITEM_ID') or "Unknown_ID"
            item_errors = []
            
            # Check mandatory tags
            for tag in mandatory_tags:
                tag_elem = elem.find(tag)
                if tag_elem is None:
                    item_errors.append(f"Missing mandatory tag: <{tag}>")
                elif not tag_elem.text or not tag_elem.text.strip():
                    item_errors.append(f"Empty mandatory tag: <{tag}>")
            
            # Check DELIVERY_DATE type
            delivery_date_elem = elem.find('DELIVERY_DATE')
            if delivery_date_elem is not None and delivery_date_elem.text and delivery_date_elem.text.strip():
                try:
                    int(delivery_date_elem.text.strip())
                except ValueError:
                    item_errors.append(f"Invalid <DELIVERY_DATE>: must be an integer, got '{delivery_date_elem.text.strip()}'")
            
            # Check EAN tag
            ean_elem = elem.find('EAN')
            if ean_elem is None:
                item_errors.append("Missing <EAN> tag")
            else:
                ean_text = ean_elem.text
                if not ean_text or not ean_text.strip():
                    item_errors.append("Empty <EAN> tag")
                else:
                    ean_clean = ean_text.strip()
                    if not ean_clean.isdigit():
                        item_errors.append(f"Malformed <EAN> tag (non-numeric): '{ean_clean}'")
                    elif len(ean_clean) == 12:
                        ean_elem.text = "0" + ean_clean
                    elif len(ean_clean) not in (8, 13):
                        item_errors.append(f"Malformed <EAN> tag (invalid length {len(ean_clean)}): '{ean_clean}'")
            
            if item_errors:
                errors.append({
                    'ITEM_ID': item_id,
                    'errors': item_errors
                })
            
            # Clear element to free memory
            elem.clear()
            # Also clear references to ancestors to avoid memory leaks
            while elem.getprevious() is not None:
                del elem.getparent()[0]
                    
    except etree.XMLSyntaxError as e:
        return {"critical_error": f"XML Syntax Error: {e}"}
    except Exception as e:
        return {"critical_error": f"An error occurred: {e}"}

    summary = {
        "total_items_parsed": total_items,
        "total_items_with_errors": len(errors),
        "item_errors": errors
    }
    
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <path_to_xml>")
        sys.exit(1)
        
    xml_file = sys.argv[1]
    print(f"Parsing {xml_file}...\n")
    results = parse_heureka_xml(xml_file)
    
    if "critical_error" in results:
        print(f"FAILED: {results['critical_error']}")
    else:
        print(f"Total items parsed: {results['total_items_parsed']}")
        print(f"Total items with errors: {results['total_items_with_errors']}\n")
        
        for error in results['item_errors']:
            print(f"ITEM_ID: {error['ITEM_ID']}")
            for msg in error['errors']:
                print(f"  - {msg}")
            print("-" * 30)
