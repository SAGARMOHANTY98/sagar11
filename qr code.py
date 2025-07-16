import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode


def create_invoice_labels():
    st.title("📦 QR Code Label Generator")
    st.markdown("Creates 65 labels per A4 sheet (38mm x 21mm each) with compact QR codes")

    # User inputs
    date = st.text_input("Enter Date (e.g., 01-07-2024)", value="01-07-2024")
    invoice_no = st.text_input("Enter Invoice Number (e.g., INV-123)", value="INV-123")
    supplier = st.text_input("Enter Supplier Name", value="Supplier Name")
    num_items = st.number_input("Number of different items", min_value=1, step=1, value=1)

    items_data = {}
    total_labels = 0

    for i in range(1, num_items + 1):
        pieces = st.number_input(f"Number of pieces for item {i}", min_value=1, step=1, value=1, key=f"pieces_{i}")
        location = st.text_input(f"Location for item {i}", value=f"Location {i}", key=f"loc_{i}")
        items_data[i] = {"pieces": pieces, "location": location}
        total_labels += pieces

    st.write(f"**Total labels to generate:** {total_labels}")

    if st.button("🖨️ Generate Labels"):
        # Image and label config
        DPI = 300
        A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297
        LABEL_WIDTH_MM, LABEL_HEIGHT_MM = 37.02, 20.99
        A4_WIDTH_PX = int(A4_WIDTH_MM / 25.4 * DPI)
        A4_HEIGHT_PX = int(A4_HEIGHT_MM / 25.4 * DPI)
        LABEL_WIDTH_PX = int(LABEL_WIDTH_MM / 25.4 * DPI)
        LABEL_HEIGHT_PX = int(LABEL_HEIGHT_MM / 25.4 * DPI)
        COLS, ROWS = 5, 13
        MAX_LABELS_PER_SHEET = COLS * ROWS

        MARGIN_LEFT_RIGHT_MM = 8
        MARGIN_TOP_BOTTOM_MM = 14.77
        H_SPACING_MM = 2
        V_SPACING_MM = 0

        MARGIN_LEFT_RIGHT_PX = int(MARGIN_LEFT_RIGHT_MM / 25.4 * DPI)
        MARGIN_TOP_BOTTOM_PX = int(MARGIN_TOP_BOTTOM_MM / 25.4 * DPI)
        h_spacing = int(H_SPACING_MM / 25.4 * DPI)
        v_spacing = int(V_SPACING_MM / 25.4 * DPI)

        start_x = MARGIN_LEFT_RIGHT_PX
        start_y = MARGIN_TOP_BOTTOM_PX

        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()

        sheet_number = 1
        label_count = 0
        sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
        draw = ImageDraw.Draw(sheet)

        for item_num, item_info in items_data.items():
            num_pieces = item_info["pieces"]
            location = item_info["location"]
            for piece_num in range(1, num_pieces + 1):
                if label_count >= MAX_LABELS_PER_SHEET:
                    buf = io.BytesIO()
                    sheet.save(buf, format="PNG", dpi=(DPI, DPI))
                    st.image(buf, caption=f"QR Labels Sheet {sheet_number}", use_container_width=True)
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

                # QR data without item and piece
                qr_data = (
                    f"DT:{date}|INV:{invoice_no}|SUP:{supplier[:15]}"
                    f"|LOC:{location[:15]}"
                )

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_Q,
                    box_size=1,
                    border=1
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

                qr_size = int(LABEL_WIDTH_PX * 0.35)  # smaller QR
                qr_img = qr_img.resize((qr_size, qr_size))

                qr_x = x + 5
                qr_y = y + (LABEL_HEIGHT_PX - qr_size) // 2
                sheet.paste(qr_img, (qr_x, qr_y))

                # Draw text (item and piece) outside QR
                text = f"Item {item_num}\nPiece {piece_num}/{num_pieces}"
                text_x = qr_x + qr_size + 5
                text_y = qr_y
                for line in text.splitlines():
                    draw.text((text_x, text_y), line, fill="black", font=font)
                    text_y += 12

                draw.rectangle([x, y, x + LABEL_WIDTH_PX - 1, y + LABEL_HEIGHT_PX - 1], outline="black", width=1)
                label_count += 1

        if label_count > 0:
            buf = io.BytesIO()
            sheet.save(buf, format="PNG", dpi=(DPI, DPI))
            st.image(buf, caption=f"QR Labels Sheet {sheet_number}", use_container_width=True)
            st.download_button(
                label=f"📥 Download Sheet {sheet_number}",
                data=buf.getvalue(),
                file_name=f"QR_Labels_Sheet_{sheet_number}.png",
                mime="image/png"
            )

        st.success(f"✅ Generated {total_labels} compact QR labels across {sheet_number} sheet(s).")


if __name__ == "__main__":
    create_invoice_labels()


