# app.py
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from matcher import find_matches

# Page config
st.set_page_config(page_title="Fido", layout="wide")
st.title("🔍 Fido!")

DATASET_PATH = "data/items_clean.csv"
IMAGES_PATH = "data/images_resized/"

# Ensure folders exist
os.makedirs(IMAGES_PATH, exist_ok=True)

def load_dataset(path=DATASET_PATH):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=["item_id", "type", "description", "image_path", "contact", "timestamp"])

def save_new_item(uploaded, desc, mode, contact, dataset_path=DATASET_PATH):
    df = load_dataset(dataset_path)

    # Generate new unique ID
    new_id = int(df["item_id"].max() + 1) if not df.empty else 1

    # Save uploaded image (if any)
    image_path = ""
    if uploaded:
        ext = os.path.splitext(uploaded.name)[1] or ".jpg"
        filename = f"{mode}{new_id}{uuid.uuid4().hex[:6]}{ext}"
        save_path = os.path.join(IMAGES_PATH, filename)

        with open(save_path, "wb") as f:
            f.write(uploaded.read())

        image_path = save_path

    # Append new row
    new_row = {
        "item_id": new_id,
        "type": mode,
        "description": desc,
        "image_path": image_path,
        "contact": contact,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(dataset_path, index=False)

    return new_row

def delete_item(item_id, dataset_path=DATASET_PATH):
    df = load_dataset(dataset_path)
    df = df[df["item_id"] != item_id]  # remove the item
    df.to_csv(dataset_path, index=False)

# 🔄 Sidebar: always load fresh dataset so it updates live
st.sidebar.header("📂 Browse Dataset")
dataset = load_dataset(DATASET_PATH)

view = st.sidebar.selectbox("Show", ["All", "Lost", "Found"], key="sidebar_view")
if view != "All":
    show_df = dataset[dataset["type"].str.lower() == view.lower()]
else:
    show_df = dataset

for _, r in show_df.iterrows():
    st.sidebar.write(f"- {r['type'].title()}: {r['description'][:60]}")
    if isinstance(r['image_path'], str) and os.path.exists(r['image_path']):
        st.sidebar.image(r['image_path'], width=80)

# Helper function to call matcher
def call_matcher(uploaded, desc, dataset):
    try:
        return find_matches(uploaded, desc, dataset)
    except Exception: # webhook testt
        pass
    try:
        tmp = "tmp_upload.jpg"
        if hasattr(uploaded, "read"):
            with open(tmp, "wb") as f:
                f.write(uploaded.read())
        elif isinstance(uploaded, str) and os.path.exists(uploaded):
            tmp = uploaded
        else:
            raise ValueError("Unsupported upload type")
        return find_matches(tmp, desc, dataset)
    finally:
        if os.path.exists("tmp_upload.jpg"):
            os.remove("tmp_upload.jpg")

# Tabs: Lost & Found
tab1, tab2 = st.tabs(["➕ Report Lost Item", "➕ Report Found Item"])

for tab, mode in [(tab1, "lost"), (tab2, "found")]:
    with tab:
        st.subheader(f"Upload {mode.title()} Item")

        uploaded = st.file_uploader("Image", type=["jpg", "jpeg", "png"], key=f"file_{mode}")
        desc = st.text_area("Description", key=f"desc_{mode}")
        contact = st.text_input("Your Contact Info (phone/email)", key=f"contact_{mode}")

        # Save button
        if st.button(f"Save {mode.title()} Item", key=f"save_{mode}"):
            if not uploaded and desc.strip() == "":
                st.warning("Please provide at least an image or a description.")
            elif not contact.strip():
                st.warning("Please provide your contact information.")
            else:
                new_item = save_new_item(uploaded, desc, mode, contact)
                st.success(f"✅ {mode.title().title()} item saved with ID {new_item['item_id']}")
                st.experimental_rerun()

        # Find matches button
        if st.button(f"Find Matches ({mode})", key=f"btn_{mode}"):
            dataset = load_dataset(DATASET_PATH)  # refresh dataset after adding
            if not uploaded and desc.strip() == "":
                st.warning("Upload an image or enter a description.")
            else:
                results = call_matcher(uploaded or "", desc, dataset)
                st.write("### 🔎 Top Matches")

                if not results:
                    st.info("No good matches found. Try another description.")
                for r in results[:3]:
                    cols = st.columns([1, 3])
                    img_path = r.get("image_path", "")
                    with cols[0]:
                        if isinstance(img_path, str) and os.path.exists(img_path):
                            st.image(img_path, width=140)
                        else:
                            st.write("No image")
                    with cols[1]:
                        st.markdown(f"{r.get('description','No desc')}")
                        st.write(f"Item ID: {r.get('item_id','-')} | Score: {round(r.get('score',0)*100,2)}%")
                        st.write(f"📞 Contact: {r.get('contact','N/A')}")
                        if st.button(f"✅ Mark as Returned (ID {r.get('item_id')})", key=f"done_{r.get('item_id')}"):
                            delete_item(r.get('item_id'))
                            st.success(f"Item {r.get('item_id')} has been marked as returned and removed from dataset.")
                            st.experimental_rerun()

                            # --- Admin Panel (Password Protected) ---
st.markdown("---")
st.header("🛠 Admin Panel")

# Simple password auth
admin_password = "admin123"  # 🔒 change this to something secure
entered_pw = st.text_input("Enter Admin Password:", type="password", key="admin_pw")

if entered_pw == admin_password:
    st.success("✅ Access granted to Admin Panel")

    admin_dataset = load_dataset(DATASET_PATH)

    admin_view = st.selectbox("Filter items", ["All", "Lost", "Found"], key="admin_view")
    if admin_view != "All":
        admin_show_df = admin_dataset[admin_dataset["type"].str.lower() == admin_view.lower()]
    else:
        admin_show_df = admin_dataset

    if admin_show_df.empty:
        st.info("No items found in this category.")
    else:
        # Show table with images + details
        for _, row in admin_show_df.iterrows():
            cols = st.columns([1, 3, 2])
            with cols[0]:
                if isinstance(row["image_path"], str) and os.path.exists(row["image_path"]):
                    st.image(row["image_path"], width=120)
                else:
                    st.write("No image")
            with cols[1]:
                st.write(f"*ID:* {row['item_id']}")
                st.write(f"*Type:* {row['type'].title()}")
                st.write(f"*Description:* {row['description']}")
                st.write(f"📞 {row['contact']}")
                st.write(f"🕒 {row['timestamp']}")
            with cols[2]:
                if st.button(f"❌ Delete {row['item_id']}", key=f"del_admin_{row['item_id']}"):
                    removed = delete_item(row["item_id"])
                    if removed:
                        st.success(f"Item {row['item_id']} deleted.")
                        st.experimental_rerun()
else:
    if entered_pw:
        st.error("❌ Incorrect password. Access denied.")
    else:
        st.info("🔒 Enter password to access Admin Panel.")