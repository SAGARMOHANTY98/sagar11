import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

# Load a font (fallback if Arial Bold is unavailable)
def get_font(size):
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except:
        return ImageFont.load_default()

def create_invoice_labels():
    st.title("📦 QR Code Label Generator (with Location per Item)")
    st.markdown("Generates 65 labels per A4 sheet (38mm x 21mm each)")

    date = st.text_input("Enter Date", "01-07-2024")
    invoice_no = st.text_input("Enter Invoice Number", "INV-123")
    supplier = st.text_input("Enter Supplier Name", "Supplier Name")
    num_items = st.number_input("Number of different items", min_value=1, step=1, value=1)

    items_data = {}
    total_labels = 0

    for i in range(1, num_items + 1):
        col1, col2 = st.columns(2)
        with col1:
            pieces = st.number_input(f"Pieces for Item {i}", min_value=1, step=1, key=f"pieces_{i}")
        with col2:
            location = st.text_input(f"Location for Item {i}", key=f"location_{i}")
        items_data[i] = {"pieces": pieces, "location": location}
        total_labels += pieces

    st.write(f"**Total labels to generate:** {total_labels}")

    if st.button("🖨️ Generate Labels"):
        DPI = 300
        A4_WIDTH_PX = int(210 / 25.4 * DPI)
        A4_HEIGHT_PX = int(297 / 25.4 * DPI)
        LABEL_WIDTH_PX = int(38 / 25.4 * DPI)
        LABEL_HEIGHT_PX = int(21 / 25.4 * DPI)
        COLS, ROWS = 5, 13
        MAX_LABELS_PER_SHEET = COLS * ROWS

        MARGIN_LEFT_RIGHT_PX = int(8 / 25.4 * DPI)
        MARGIN_TOP_BOTTOM_PX = int(14.77 / 25.4 * DPI)
        h_spacing = int(2 / 25.4 * DPI)
        v_spacing = 0

        start_x = MARGIN_LEFT_RIGHT_PX
        start_y = MARGIN_TOP_BOTTOM_PX

        sheet_number = 1
        label_count = 0
        sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
        draw = ImageDraw.Draw(sheet)

        font_small = get_font(16)
        font_big = get_font(26)

        for item_num, info in items_data.items():
            num_pieces = info["pieces"]
            location = info["location"]
            for piece_num in range(1, num_pieces + 1):
                if label_count >= MAX_LABELS_PER_SHEET:
                    buf = io.BytesIO()
                    sheet.save(buf, format="PNG", dpi=(DPI, DPI))
                    st.image(buf, caption=f"Sheet {sheet_number}", use_container_width=True)
                    st.download_button(
                        label=f"📥 Download Sheet {sheet_number}",
                        data=buf.getvalue(),
                        file_name=f"QR_Labels_Sheet_{sheet_number}.png",
                        mime="image/png"
                    )
                    sheet_number += 1
                    sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
                    draw = ImageDraw.Draw(sheet)
                    label_count = 0

                col = label_count % COLS
                row = label_count // COLS
                x = start_x + col * (LABEL_WIDTH_PX + h_spacing)
                y = start_y + row * (LABEL_HEIGHT_PX + v_spacing)

                # Prepare QR data
                qr_data = f"DT:{date}|INV:{invoice_no}|SUP:{supplier}|LOC:{location}"
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_Q,
                    box_size=2,
                    border=1
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

                # Resize QR code
                qr_size = int(LABEL_WIDTH_PX * 0.35)
                qr_img = qr_img.resize((qr_size, qr_size))

                # Center QR code in the label
                qr_x = x + (LABEL_WIDTH_PX - qr_size) // 2
                qr_y = y + (LABEL_HEIGHT_PX - qr_size) // 2 + 4
                sheet.paste(qr_img, (qr_x, qr_y))

                # Draw Item and Piece (above QR)
                item_text = f"ITEM: {item_num}"
                piece_text = f"PIECE: {piece_num}/{num_pieces}"
                draw.text((x + 4, y + 2), item_text, font=font_big, fill="black")
                draw.text((x + 4, y + 4 + font_big.getbbox(item_text)[3]), piece_text, font=font_big, fill="black")

                # Draw label border
                draw.rectangle([x, y, x + LABEL_WIDTH_PX - 1, y + LABEL_HEIGHT_PX - 1], outline="black", width=1)

                label_count += 1

        # Final sheet (if not already saved)
        if label_count > 0:
            buf = io.BytesIO()
            sheet.save(buf, format="PNG", dpi=(DPI, DPI))
            st.image(buf, caption=f"Sheet {sheet_number}", use_container_width=True)
            st.download_button(
                label=f"📥 Download Sheet {sheet_number}",
                data=buf.getvalue(),
                file_name=f"QR_Labels_Sheet_{sheet_number}.png",
                mime="image/png"
            )

        st.success(f"✅ Generated {total_labels} labels across {sheet_number} sheet(s).")

if __name__ == "__main__":
    create_invoice_labels()
