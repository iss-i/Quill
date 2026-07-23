REPORT zsmpl_pp_load_res.
*&---------------------------------------------------------------------*
*& ZSMPL_PP_LOAD_RES  -  Load program for table ZTC_PP_RES
*&   SiMPL Process Parameter - Resource master
*& Package : ZSMPL_AZP2
*&
*& Loads a delimited text file - COMMA (*.csv) or TAB (*.txt); the
*& delimiter is auto-detected from the header row and the file is read
*& as UTF-8. Columns are matched to table fields by HEADER NAME (row 1),
*& so column order does not matter and extra columns are ignored.
*& Excel "quoted" fields are supported. Expected header columns:
*&     RESOURCE_ID   RESOURCE_DESC   WERKS   UOP_ID
*&
*& p_test = 'X' (default) simulates - nothing is written to the table.
*& p_del  = 'X' deletes ALL existing rows before load (update mode only).
*& p_head = number of leading rows to skip (row 1 = header, default 1).
*&---------------------------------------------------------------------*
* NOTE: gv_title is declared automatically by SELECTION-SCREEN ... TITLE
* below - do NOT add a DATA gv_title (that raises "already declared").
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE gv_title.
PARAMETERS: p_file TYPE string LOWER CASE OBLIGATORY,
            p_head TYPE i DEFAULT 1,
            p_del  TYPE abap_bool AS CHECKBOX DEFAULT space,
            p_test TYPE abap_bool AS CHECKBOX DEFAULT 'X'.
SELECTION-SCREEN END OF BLOCK b1.

DATA: gt_raw  TYPE string_table,
      gt_data TYPE STANDARD TABLE OF ztc_pp_res,
      gs_data TYPE ztc_pp_res,
      gv_read TYPE i, gv_ins TYPE i, gv_upd TYPE i, gv_err TYPE i.

INITIALIZATION.
  gv_title = 'Load ZTC_PP_RES (Resource master)'.

AT SELECTION-SCREEN ON VALUE-REQUEST FOR p_file.
  PERFORM f4_file.

START-OF-SELECTION.
  PERFORM upload.
  PERFORM parse.
  PERFORM post.
  PERFORM log.

*&--- front-end file picker (F4) -------------------------------------*
FORM f4_file.
  DATA: lt_files TYPE filetable, lv_rc TYPE i, lv_act TYPE i.
  cl_gui_frontend_services=>file_open_dialog(
    EXPORTING file_filter = 'Text/CSV (*.txt;*.csv)|*.txt;*.csv|All (*.*)|*.*'
    CHANGING  file_table = lt_files rc = lv_rc user_action = lv_act
    EXCEPTIONS OTHERS = 1 ).
  IF sy-subrc = 0 AND lv_act = cl_gui_frontend_services=>action_ok
     AND lt_files IS NOT INITIAL.
    p_file = lt_files[ 1 ]-filename.
  ENDIF.
ENDFORM.

*&--- read the file from the front end (UTF-8) -----------------------*
FORM upload.
  cl_gui_frontend_services=>gui_upload(
    EXPORTING filename = p_file filetype = 'ASC' codepage = '4110'
    CHANGING  data_tab = gt_raw
    EXCEPTIONS OTHERS = 1 ).
  IF sy-subrc <> 0.
    MESSAGE 'File could not be read from the front end' TYPE 'E'.
  ENDIF.
ENDFORM.

*&--- parse delimited lines (header-mapped, comma or tab) ------------*
FORM parse.
  DATA: lt_head TYPE string_table,
        lt_cell TYPE string_table,
        lv_line TYPE string, lv_val TYPE string, lv_hdr TYPE string,
        lv_sep  TYPE c LENGTH 1.
  DATA: BEGIN OF ls_map, name TYPE string, idx TYPE i, END OF ls_map.
  DATA lt_map LIKE SORTED TABLE OF ls_map WITH UNIQUE KEY name.
  FIELD-SYMBOLS <fs> TYPE any.

  CHECK p_head >= 1 AND lines( gt_raw ) > p_head.
  IF gt_raw[ 1 ] CS cl_abap_char_utilities=>horizontal_tab.
    lv_sep = cl_abap_char_utilities=>horizontal_tab.
  ELSE.
    lv_sep = ','.
  ENDIF.
  lv_hdr = gt_raw[ 1 ].
  PERFORM split_line USING lv_hdr lv_sep CHANGING lt_head.
  LOOP AT lt_head INTO lv_val.
    ls_map-name = to_upper( lv_val ). CONDENSE ls_map-name.
    ls_map-idx  = sy-tabix.
    INSERT ls_map INTO TABLE lt_map.
  ENDLOOP.

  DATA(lo_sd) = CAST cl_abap_structdescr(
                  cl_abap_typedescr=>describe_by_data( gs_data ) ).
  LOOP AT gt_raw INTO lv_line.
    IF sy-tabix <= p_head. CONTINUE. ENDIF.
    REPLACE ALL OCCURRENCES OF |\r| IN lv_line WITH ''.
    IF lv_line IS INITIAL OR lv_line CO ' '. CONTINUE. ENDIF.
    PERFORM split_line USING lv_line lv_sep CHANGING lt_cell.
    CLEAR gs_data.
    LOOP AT lo_sd->components INTO DATA(ls_c).
      READ TABLE lt_map WITH KEY name = ls_c-name INTO ls_map.
      IF sy-subrc <> 0. CONTINUE. ENDIF.
      READ TABLE lt_cell INDEX ls_map-idx INTO lv_val.
      IF sy-subrc <> 0. CONTINUE. ENDIF.
      ASSIGN COMPONENT ls_c-name OF STRUCTURE gs_data TO <fs>.
      IF sy-subrc <> 0. CONTINUE. ENDIF.
      PERFORM set_value USING ls_c-name lv_val CHANGING <fs>.
    ENDLOOP.
    IF gs_data-resource_id IS INITIAL. CONTINUE. ENDIF.
    APPEND gs_data TO gt_data. ADD 1 TO gv_read.
  ENDLOOP.
ENDFORM.

*&--- quote-aware line splitter (CSV/TSV, handles "quoted" fields) ---*
FORM split_line USING iv_line TYPE csequence iv_sep TYPE c
                CHANGING ct TYPE string_table.
  DATA: lv_len TYPE i, lv_i TYPE i, lv_c TYPE c LENGTH 1,
        lv_fld TYPE string, lv_q TYPE abap_bool.
  CLEAR ct.
  lv_len = strlen( iv_line ).
  WHILE lv_i < lv_len.
    lv_c = iv_line+lv_i(1).
    IF lv_q = abap_true.
      IF lv_c = '"'.
        IF lv_i + 1 < lv_len AND iv_line+lv_i(2) = '""'.
          CONCATENATE lv_fld '"' INTO lv_fld RESPECTING BLANKS.
          lv_i = lv_i + 1.
        ELSE.
          lv_q = abap_false.
        ENDIF.
      ELSE.
        CONCATENATE lv_fld lv_c INTO lv_fld RESPECTING BLANKS.
      ENDIF.
    ELSE.
      IF lv_c = '"'.
        lv_q = abap_true.
      ELSEIF lv_c = iv_sep.
        APPEND lv_fld TO ct. CLEAR lv_fld.
      ELSE.
        CONCATENATE lv_fld lv_c INTO lv_fld RESPECTING BLANKS.
      ENDIF.
    ENDIF.
    lv_i = lv_i + 1.
  ENDWHILE.
  APPEND lv_fld TO ct.
ENDFORM.

*&--- field conversion by field name --------------------------------*
FORM set_value USING iv_name TYPE csequence iv_val TYPE csequence
               CHANGING cv TYPE any.
  DATA: lv TYPE string, lu TYPE string.
  lv = iv_val.
  REPLACE ALL OCCURRENCES OF |\r| IN lv WITH ''.
  REPLACE ALL OCCURRENCES OF |\n| IN lv WITH ''.
  SHIFT lv LEFT DELETING LEADING space.
  CASE iv_name.
    WHEN 'MATNR'.
      IF lv = '*' OR lv IS INITIAL.
        cv = lv.
      ELSE.
        CALL FUNCTION 'CONVERSION_EXIT_MATN1_INPUT'
          EXPORTING input = lv IMPORTING output = cv
          EXCEPTIONS OTHERS = 0.
      ENDIF.
    WHEN 'IS_CALC' OR 'TOOL_READY'.
      lu = to_upper( lv ).
      IF lu = 'X' OR lu = 'Y' OR lu = 'YES' OR lu = 'TRUE' OR lu = '1'.
        cv = 'X'.
      ELSE.
        cv = space.
      ENDIF.
    WHEN 'VALID_FROM' OR 'VALID_TO' OR 'CREATED_ON' OR 'CHANGED_ON'.
      REPLACE ALL OCCURRENCES OF '-' IN lv WITH ''.
      REPLACE ALL OCCURRENCES OF '/' IN lv WITH ''.
      REPLACE ALL OCCURRENCES OF '.' IN lv WITH ''.
      CONDENSE lv NO-GAPS.
      IF strlen( lv ) = 8. cv = lv. ELSE. CLEAR cv. ENDIF.
    WHEN OTHERS.
      cv = lv.
  ENDCASE.
ENDFORM.

*&--- upsert (MODIFY) into the table ---------------------------------*
FORM post.
  IF p_del = abap_true AND p_test = abap_false.
    DELETE FROM ztc_pp_res.
  ENDIF.
  LOOP AT gt_data INTO gs_data.
    SELECT SINGLE resource_id FROM ztc_pp_res INTO @DATA(lv_x)
      WHERE resource_id = @gs_data-resource_id.
    IF sy-subrc = 0. ADD 1 TO gv_upd. ELSE. ADD 1 TO gv_ins. ENDIF.
    IF p_test = abap_false.
      MODIFY ztc_pp_res FROM gs_data.
      IF sy-subrc <> 0. ADD 1 TO gv_err. ENDIF.
    ENDIF.
  ENDLOOP.
  IF p_test = abap_false. COMMIT WORK AND WAIT. ENDIF.
ENDFORM.

*&--- summary log ----------------------------------------------------*
FORM log.
  WRITE: / 'Table       : ZTC_PP_RES'.
  WRITE: / 'File        :', p_file.
  IF p_test = abap_true.
    WRITE: / 'Mode        : TEST (simulation - nothing written)'.
  ELSE.
    WRITE: / 'Mode        : UPDATE (records committed)'.
  ENDIF.
  WRITE: / 'Rows read   :', gv_read.
  WRITE: / '  new       :', gv_ins.
  WRITE: / '  existing  :', gv_upd.
  WRITE: / '  errors    :', gv_err.
ENDFORM.
