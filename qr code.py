import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

def get_font(size):
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)

def create_invoice_labels():
    st.title("📦 QR Code Label Generator")
    st.markdown("Creates 65 labels per A4 sheet (38mm x 21mm each) with QR codes and readable item/piece info")

    # User inputs
    date = st.text_input("Enter Date", value="01-07-2024")
    invoice_no = st.text_input("Enter Invoice Number", value="INV-123")
    supplier = st.text_input("Enter Supplier Name", value="Supplier Name")
    num_items = st.number_input("Number of different items", min_value=1, step=1, value=1)

    items_data = {}
    total_labels = 0

    for i in range(1, num_items + 1):
        col1, col2 = st.columns(2)
        with col1:
            pieces = st.number_input(f"Pieces for item {i}", min_value=1, step=1, value=1, key=f"pieces_{i}")
        with col2:
            location = st.text_input(f"Location for item {i}", key=f"loc_{i}")
        items_data[i] = {'pieces': pieces, 'location': location}
        total_labels += pieces

    st.write(f"**Total labels to generate:** {total_labels}")

    if st.button("🖨️ Generate Labels"):
        # Page & label setup
        DPI = 300
        A4_WIDTH_PX = int(210 / 25.4 * DPI)
        A4_HEIGHT_PX = int(297 / 25.4 * DPI)
        LABEL_WIDTH_PX = int(37.02 / 25.4 * DPI)
        LABEL_HEIGHT_PX = int(20.99 / 25.4 * DPI)
        COLS, ROWS = 5, 13
        MAX_LABELS_PER_SHEET = COLS * ROWS
        MARGIN_X = int(8 / 25.4 * DPI)
        MARGIN_Y = int(14.77 / 25.4 * DPI)
        SPACING_X = int(2 / 25.4 * DPI)

        font_small = get_font(12)  # ✅ Smaller font for item/piece
        sheet_number = 1
        label_count = 0
        sheet = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
        draw = ImageDraw.Draw(sheet)

        for item_num, info in items_data.items():
            num_pieces = info['pieces']
            location = info['location']

            for piece_num in range(1, num_pieces + 1):
                if label_count >= MAX_LABELS_PER_SHEET:
                    # Save & show sheet
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
                x = MARGIN_X + col * (LABEL_WIDTH_PX + SPACING_X)
                y = MARGIN_Y + row * LABEL_HEIGHT_PX

                # Create compact QR
                qr_data = f"DT:{date}|INV:{invoice_no}|SUP:{supplier[:15]}|LOC:{location}"
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_Q,
                    box_size=2,
                    border=1
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                qr_size = int(LABEL_WIDTH_PX * 0.42)
                qr_img = qr_img.resize((qr_size, qr_size))

                # Paste QR center
                qr_x = x + (LABEL_WIDTH_PX - qr_size) // 2
                qr_y = y + (LABEL_HEIGHT_PX - qr_size) // 2 - 4
                sheet.paste(qr_img, (qr_x, qr_y))

                # ✅ ITEM & PIECE text (small font, right of QR)
                text_item = f"ITEM: {item_num}"
                text_piece = f"PIECE: {piece_num}/{num_pieces}"
                text_x = x + LABEL_WIDTH_PX * 0.5
                text_y_item = y + 3
                text_y_piece = text_y_item + 16
                draw.text((text_x, text_y_item), text_item, font=font_small, fill="black")
                draw.text((text_x, text_y_piece), text_piece, font=font_small, fill="black")

                # Border
                draw.rectangle([x, y, x + LABEL_WIDTH_PX - 1, y + LABEL_HEIGHT_PX - 1], outline="black", width=1)

                label_count += 1

        # Last page save
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

        st.success(f"✅ Generated {total_labels} labels across {sheet_number} sheet(s)")

if __name__ == "__main__":
    create_invoice_labels()


