import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

# Font helper
def get_font(size):
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)

def create_invoice_labels():
    st.title("📦 QR Code Label Generator with Locations")
    st.markdown("Generates 65 labels per A4 sheet (38mm x 21mm each)")

    # Inputs
    date = st.text_input("Enter Date (e.g., 01-07-2024)", value="01-07-2024")
    invoice_no = st.text_input("Enter Invoice Number (e.g., INV-123)", value="INV-123")
    supplier = st.text_input("Enter Supplier Name", value="Supplier Name")
    num_items = st.number_input("Number of different items", min_value=1, step=1, value=1)

    items_data = {}
    total_labels = 0

    for i in range(1, num_items + 1):
        col1, col2 = st.columns(2)
        with col1:
            pieces = st.number_input(f"Pieces for Item {i}", min_value=1, step=1, value=1, key=f"pieces_{i}")
        with col2:
            location = st.text_input(f"Location for Item {i}", value=f"Loc-{i}", key=f"loc_{i}")
        items_data[i] = {"pieces": pieces, "location": location}
        total_labels += pieces

    st.write(f"**Total labels to generate:** {total_labels}")

    if st.button("🖨️ Generate Labels"):
        DPI = 300
        A4_W_MM, A4_H_MM = 210, 297
        LABEL_W_MM, LABEL_H_MM = 37.02, 20.99
        A4_W_PX = int(A4_W_MM / 25.4 * DPI)
        A4_H_PX = int(A4_H_MM / 25.4 * DPI)
        LABEL_W_PX = int(LABEL_W_MM / 25.4 * DPI)
        LABEL_H_PX = int(LABEL_H_MM / 25.4 * DPI)

        COLS, ROWS = 5, 13
        MAX_LABELS = COLS * ROWS

        MARGIN_LR_MM, MARGIN_TB_MM = 8, 14.77
        H_SPACING_MM, V_SPACING_MM = 2, 0
        MARGIN_LR_PX = int(MARGIN_LR_MM / 25.4 * DPI)
        MARGIN_TB_PX = int(MARGIN_TB_MM / 25.4 * DPI)
        h_spacing = int(H_SPACING_MM / 25.4 * DPI)
        v_spacing = int(V_SPACING_MM / 25.4 * DPI)

        start_x = MARGIN_LR_PX
        start_y = MARGIN_TB_PX

        sheet_number = 1
        label_count = 0
        sheet = Image.new("RGB", (A4_W_PX, A4_H_PX), "white")
        draw = ImageDraw.Draw(sheet)

        font_medium = get_font(22)  # Smaller than previous 30

        for item_num, item_data in items_data.items():
            num_pieces = item_data["pieces"]
            location = item_data["location"]

            for piece_num in range(1, num_pieces + 1):
                if label_count >= MAX_LABELS:
                    buf = io.BytesIO()
                    sheet.save(buf, format="PNG", dpi=(DPI, DPI))
                    sheet_data = buf.getvalue()
                    st.image(buf, caption=f"QR Labels Sheet {sheet_number}", use_container_width=True)
                    st.download_button(f"📥 Download Sheet {sheet_number}", sheet_data,
                                       file_name=f"QR_Labels_Sheet_{sheet_number}.png", mime="image/png")

                    sheet_number += 1
                    sheet = Image.new("RGB", (A4_W_PX, A4_H_PX), "white")
                    draw = ImageDraw.Draw(sheet)
                    label_count = 0

                col = label_count % COLS
                row = label_count // COLS
                x = start_x + col * (LABEL_W_PX + h_spacing)
                y = start_y + row * (LABEL_H_PX + v_spacing)

                # Generate QR
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

                qr_size = int(LABEL_W_PX * 0.44)
                qr_img = qr_img.resize((qr_size, qr_size))
                qr_x = x + (LABEL_W_PX - qr_size) // 2
                qr_y = y + (LABEL_H_PX - qr_size) // 2
                sheet.paste(qr_img, (qr_x, qr_y))

                # Draw ITEM and PIECE outside QR
                item_text = f"ITEM: {item_num}"
                piece_text = f"PIECE: {piece_num}/{num_pieces}"
                text_x = x + 20
                text_y = y + 4

                draw.text((text_x, text_y), item_text, font=font_medium, fill="black")
                draw.text((text_x, text_y + font_medium.getbbox(item_text)[3] + 2), piece_text, font=font_medium, fill="black")

                draw.rectangle([x, y, x + LABEL_W_PX - 1, y + LABEL_H_PX - 1], outline="black", width=1)
                label_count += 1

        if label_count > 0:
            buf = io.BytesIO()
            sheet.save(buf, format="PNG", dpi=(DPI, DPI))
            sheet_data = buf.getvalue()
            st.image(buf, caption=f"QR Labels Sheet {sheet_number}", use_container_width=True)
            st.download_button(f"📥 Download Sheet {sheet_number}", sheet_data,
                               file_name=f"QR_Labels_Sheet_{sheet_number}.png", mime="image/png")

        st.success(f"✅ Generated {total_labels} labels across {sheet_number} sheet(s).")

if __name__ == "__main__":
    create_invoice_labels()

