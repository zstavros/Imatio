# Προσθήκη επιλογής "-- Επιλέξτε Είδος --" στην αρχή
        col_name_key = 'ItName' if 'ItName' in df_items.columns else 'Name'
        raw_items = df_items[col_name_key].dropna().tolist() if not df_items.empty and col_name_key in df_items.columns else ["Παντελόνι", "Πουκάμισο", "Μπλούζα", "Μπουφάν"]
        item_choices = ["-- Επιλέξτε Είδος --"] + raw_items

        st.markdown("<p style='font-size: 0.95rem; font-weight: bold; margin-bottom: 2px;'>Καταχώρηση Ειδών & Θέσεων (Προσθέστε γραμμές +):</p>", unsafe_allow_html=True)

        # Τελεία κενός πίνακας στην αρχή
        if "editor_df" not in st.session_state:
            st.session_state.editor_df = pd.DataFrame(
                columns=["Είδος", "Θέση / Ράφι", "Κόστος (€)"]
            )

        # Data editor με κενές γραμμές
        edited_df = st.data_editor(
            st.session_state.editor_df,
            num_rows="dynamic",
            column_config={
                "Είδος": st.column_config.SelectboxColumn(
                    "Είδος",
                    options=item_choices,
                    required=True,
                    default="-- Επιλέξτε Είδος --"
                ),
                "Θέση / Ράφι": st.column_config.TextColumn("Θέση / Ράφι", required=False),
                "Κόστος (€)": st.column_config.NumberColumn("Κόστος (€)", min_value=0.0, step=0.5, default=0.0)
            },
            key="multi_items_editor",
            use_container_width=True
        )
