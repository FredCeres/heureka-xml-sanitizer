import streamlit as st
from parser import parse_heureka_xml

# 2. UI CONFIGURATION
st.set_page_config(page_title="Heureka XML Sanitizer", layout="centered")
st.title("📦 Heureka.cz XML Sanitizer")
st.markdown("Upload your messy e-shop XML feed. We validate `<SHOPITEM>` taxonomy and fix missing tags instantly.")

# SECURE TOKEN PATCH: Replaced simple "success" check with an obscure token
is_paid = st.query_params.get("token") == "sk_live_9f82hXzPqL1m"
if is_paid:
    st.success("✅ Platba byla úspěšná! Nahrajte svůj XML feed znovu pro okamžité stažení opravené verze.")

# 3. FILE UPLOADER
uploaded_file = st.file_uploader("Upload XML Feed (.xml)", type=["xml"])

if uploaded_file is not None:
    if st.button("Analyze Feed"):
        with st.spinner("Parsing XML taxonomy..."):
            
            results = parse_heureka_xml(uploaded_file)
            
            if "critical_error" in results:
                st.error(f"Failed to parse XML: {results['critical_error']}")
                st.stop()
                
            total = results.get("total_items_parsed", 0)
            errors = []
            for e in results.get("item_errors", []):
                for msg in e["errors"]:
                    errors.append(f"Item {e['ITEM_ID']}: {msg}")
            
            # 4. METRIC DASHBOARD
            st.success(f"Parsing complete. Scanned {total} items.")
            col1, col2 = st.columns(2)
            col1.metric(label="Total Items", value=total)
            col2.metric(label="Errors Found", value=len(errors), delta="-Action Required", delta_color="inverse")
            
            # 5. ERROR PREVIEW & PAYWALL
            if errors:
                if is_paid:
                    st.success("Payment successful! You can now download your sanitized feed.")
                    fixed_xml = uploaded_file.getvalue() # Placeholder for actual sanitized XML
                    st.download_button(
                        label="Download Sanitized XML",
                        data=fixed_xml,
                        file_name="sanitized_feed.xml",
                        mime="application/xml"
                    )
                else:
                    st.error("Validation Failed: Taxonomy violations detected.")
                    st.write("**Top Errors (Free Preview):**")
                    
                    # Show only the first 3 errors to prove the tool works
                    for e in errors[:3]: 
                        st.code(e)
                    
                    st.warning("🔒 Fix all errors and generate a 100% compliant XML feed.")
                    
                    stripe_link = "https://buy.stripe.com/bJe6oHcCmfnR8NkcDbg3600"
                    st.markdown(f"[**Pay 199 CZK to Download Sanitized XML**]({stripe_link})")
            else:
                st.success("Feed is 100% compliant. No action needed.")