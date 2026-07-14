FUNCTION zsmpl_fm_attachment_save_ebr.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_ORDER) TYPE  AUFNR
 *"     REFERENCE(IM_MATNR) TYPE  MATNR18 OPTIONAL
 *"     REFERENCE(IM_CHARG) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(IM_FILENAME) TYPE  CHAR30 OPTIONAL
 *"     REFERENCE(IM_INDEX) TYPE  I OPTIONAL
 *"     REFERENCE(IT_EXP_ATT_MADE) TYPE  /SMPL/STR_TT_TEXT30 OPTIONAL
 *"     REFERENCE(IT_BINARY) TYPE  TABL1024_T OPTIONAL
 *"     REFERENCE(IM_ATT_TYPE) TYPE  CHAR2 OPTIONAL
 *"     REFERENCE(IM_FILESIZE) TYPE  I OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EX_FILENAME) TYPE  TEXT30
 *"     REFERENCE(EX_VAL_FLAG) TYPE  I
 *"  CHANGING
 *"     REFERENCE(CT_FILE_LIST) TYPE  /SMPL/STR_TT_TEXT30 OPTIONAL
 *"     REFERENCE(CT_CREATED_BY) TYPE  /SMPL/STR_TT_TEXT30 OPTIONAL
 *"     REFERENCE(CT_CREATED_DATE) TYPE  /SMPL/STR_TT_DATS OPTIONAL
 *"     REFERENCE(CT_CREATED_TIME) TYPE  /SMPL/STR_TT_TIMS OPTIONAL
 *"     REFERENCE(CT_STATUS) TYPE  /SMPL/STR_TT_TEXT30 OPTIONAL
 *"     REFERENCE(CT_EXP_ATT) TYPE  /SMPL/STR_TT_TEXT30 OPTIONAL
 *"  EXCEPTIONS
 *"      INSPECTION_LOT_MISSING
 *"      GOS_UTIL_NOT_INITIALIZED
 *"      LOAD_ATTACHMENTS_ERROR
 *"      SAVE_ATTACHMENTS_ERROR
 *"      FILE_CONVERSION_ERROR
 *"      FILE_LOAD_ERROR
 *"----------------------------------------------------------------------
 *======================================================================*
 * Program Name: ZSMPL_FM_ATTACHMENT_SAVE_EBR                           *
 * Author      : MKIRK                                                  *
 * Description : Save a new attachment in the generic attachment xstep  *
 *               in EBR                                                 *
 *                                                                      *
 * Date Created: 07/09/2025                                             *
 *======================================================================*
 
  CONSTANTS lc_error TYPE string VALUE 'E' ##NO_TEXT.
 
  CONSTANTS: lc_error_upload    TYPE i VALUE '-1'.
 
  DATA: lo_attach_service     TYPE REF TO /smpl/pppi_cl_attach_gos.
 
  DATA:
     ls_error_msg     TYPE symsg,
     l_aufnr          TYPE aufnr,
     lv_rc            TYPE i,
     lt_filetable     TYPE filetable,
     ls_file          TYPE file_table,
     lt_error_msg     LIKE STANDARD TABLE OF symsg,
     lt_file_list     TYPE /smpl/str_tt_text30,
     ls_file_list     TYPE LINE OF /smpl/str_tt_text30,
     lt_created_by    TYPE /smpl/str_tt_text30,
     lt_created_date  TYPE /smpl/str_tt_dats,
     lt_created_time  TYPE /smpl/str_tt_tims,
     lt_status        TYPE /smpl/str_tt_text30,
     lv_loop          TYPE i,
     lv_bin_length    TYPE i,
     lt_raw_data      TYPE STANDARD TABLE OF raw255,
     lv_xstring       TYPE xstring,
     lv_filename      TYPE string,
     lv_filename_base TYPE string,
     lt_allowed_types TYPE STANDARD TABLE OF string,
     lt_stat       TYPE /smpl/str_tt_text30.
 
  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
   DATA: lo_socket    TYPE REF TO /smpl/ebr_cl_web_sock_hndl.
   "20260302 Add message KWVP774
   DATA: ls_prepare_msg_frontend TYPE /SMPL/EBR_PREP_MSG_FRONTEND. "Message review changes
   DATA: lv_string_msg TYPE string.
   "20260302 Add message KWVP774
 
  CREATE OBJECT lo_socket.
 
  " Use order number for attachments
   "Check if order exists
   IF im_order IS NOT INITIAL.
     l_aufnr = im_order.
   ELSE.
     MESSAGE TEXT-001 TYPE lc_error RAISING inspection_lot_missing.
   ENDIF.
 

  " Get service instance for current inspection lot
   PERFORM get_service_instance
     USING
       l_aufnr
     CHANGING
       lo_attach_service.
 
*   Get file from frontent via upload
 
  CREATE OBJECT lo_socket.
   IF  lcl_websocket->gv_function = 'SMPL_EBR'.
     IF lcl_websocket->gs_upload-filename IS INITIAL.
       CONCATENATE  '<input name="showAttachment" value="show_attachment_dialog">'
 *                   '<input name="fileName" value="">'                            "++Manu
                    '<input name ="AttachmentType" value="PO">'
                     lcl_websocket->gv_request_string INTO DATA(lv_string).
 
      lo_socket->send_message( i_application_id = '/SMPL/EBR_AMC_MC'   "+PAM
                                i_channel_id     = '/ui5'
                                i_string         = lv_string
                                i_unique_id      = lcl_websocket->gv_unique_id ).
 
    ELSEIF  lcl_websocket->gs_upload-filename IS NOT INITIAL.
       ls_file-filename = lcl_websocket->gs_upload-filename.
     ENDIF.
 
  ELSEIF im_att_type EQ 'PO'.
     ls_file-filename = im_filename.
     lv_bin_length = im_filesize.
   ELSE.
 
    cl_gui_frontend_services=>file_open_dialog(
       CHANGING
         file_table = lt_filetable
         rc = lv_rc ).
     IF lv_rc = lc_error_upload.
 *     File transfer failed
       IF 1 = 0.
         MESSAGE e044(w3_tool).
       ENDIF.
       CLEAR ls_error_msg.
       ls_error_msg-msgty = 'E'.
       ls_error_msg-msgid = 'W3_TOOL'.
       ls_error_msg-msgno = '044'.
       INSERT ls_error_msg INTO TABLE lt_error_msg.
       RETURN.
     ENDIF.
 *   File length: 1024 CHARs
     IF lines( lt_filetable ) NE 1.
 *     Don't support upload of multiple files
       RETURN.
     ELSE.
       READ TABLE lt_filetable INTO ls_file INDEX 1.
     ENDIF.
   ENDIF.
 

*  ************************************
   "JCRAIG File Upload Change/MOD  20250507 start
 
  lv_filename = ls_file-filename.
   IF lv_filename IS NOT INITIAL.
     " Remove the extension (after the dot)
 *    SPLIT lv_filename AT '.' INTO lv_filename_base DATA(lv_ext).
     DATA(lv_ext)  = to_lower( substring_after( val = lv_filename sub = '.' occ = -1 ) ).
     lv_filename_base = substring_before( val = lv_filename sub = '.' occ = -1 ).
 

    " Check & Define allowed file types
     APPEND 'pdf'  TO lt_allowed_types.
     APPEND 'docx' TO lt_allowed_types.
     APPEND 'xlsx' TO lt_allowed_types.
     APPEND 'jpeg' TO lt_allowed_types.
     APPEND 'jpg'  TO lt_allowed_types.
 
    " Get file extension in lowercase
     TRANSLATE lv_ext TO LOWER CASE.
 
    " Check if extension is allowed
     READ TABLE lt_allowed_types WITH TABLE KEY table_line = lv_ext TRANSPORTING NO FIELDS.
     IF sy-subrc <> 0.
       IF lcl_websocket->gv_function = 'SMPL_EBR'.
         lv_string_msg = TEXT-007.
         ls_prepare_msg_frontend-message_custom = abap_true.
         ls_prepare_msg_frontend-message_source = '2'.
         ls_prepare_msg_frontend-message_type = 'W'.
         ls_prepare_msg_frontend-message_text = lv_string_msg.
         CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
           EXPORTING
             is_prepare_message = ls_prepare_msg_frontend.
         RAISE file_load_error.
       ELSE.
       MESSAGE TEXT-007 TYPE 'S' DISPLAY LIKE 'E'.
       RAISE file_load_error.
       ENDIF.
     ENDIF.
 
    "Check if same attachment has been uploaded
     " Extract the filename only from full path w/o ext
     SPLIT lv_filename_base AT '\' INTO TABLE DATA(lt_parts).
     READ TABLE lt_parts INTO lv_filename_base INDEX lines( lt_parts ).
 
    data : lt_notes type string_t.
 
    CALL FUNCTION '/SMPL/PPPI_FM_ATTCH_GET'
       EXPORTING
         im_order                 = im_order
         im_matnr                 = im_matnr
         im_charg                 = im_charg
         it_exp_att               = it_exp_att_made
       IMPORTING
         et_file_list             = lt_file_list
 *       et_created_by            = lt_created_by
 *       et_created_date          = lt_created_date
 *       et_created_time          = lt_created_time
         et_status                = lt_stat
         et_notes                 = lt_notes
       EXCEPTIONS
         inspection_lot_missing   = 1
         load_attachments_error   = 2
         gos_util_not_initialized = 3
         OTHERS                   = 4.
 
    IF sy-subrc = 0.
       LOOP AT lt_file_list INTO DATA(lv_uploaded_files).
         IF lv_uploaded_files = lv_filename_base AND lt_stat[ sy-tabix ] <> 'DELETED'.
           MESSAGE TEXT-006 TYPE 'S' DISPLAY LIKE 'E'.
           RAISE save_attachments_error.
         ENDIF.
       ENDLOOP.
     ELSE.
       "First upload - continue.
     ENDIF.
     CLEAR lt_file_list.
 

    IF im_att_type IS INITIAL.
       " Check for duplicate uploads in current attachment
       IF im_filename IS INITIAL AND ct_file_list IS INITIAL.
         "CONTINUE
       ELSEIF im_filename IS INITIAL AND ct_file_list IS NOT INITIAL.
         IF im_index IS NOT INITIAL.
           IF ct_file_list[ im_index ] IS NOT INITIAL.
             MESSAGE TEXT-006 TYPE 'S' DISPLAY LIKE 'E'.
             RAISE save_attachments_error.
           ENDIF.
         ENDIF.
       ELSEIF im_filename IS NOT INITIAL.
         MESSAGE TEXT-006 TYPE 'S' DISPLAY LIKE 'E'.
         RAISE save_attachments_error.
       ENDIF.
 

      " Upload the file in binary mode
       CALL METHOD cl_gui_frontend_services=>gui_upload
         EXPORTING
           filename   = lv_filename
           filetype   = 'BIN'
         IMPORTING
           filelength = lv_bin_length
         CHANGING
           data_tab   = lt_raw_data
         EXCEPTIONS
           OTHERS     = 1.
 
      IF sy-subrc <> 0.
         " handle error
         RETURN.
       ENDIF.
 
      " Convert RAW255 data to XSTRING
       CALL FUNCTION 'SCMS_BINARY_TO_XSTRING'
         EXPORTING
           input_length = lv_bin_length
         IMPORTING
           buffer       = lv_xstring
         TABLES
           binary_tab   = lt_raw_data.
 
*else block for Po attachments
     ELSE.
       CALL FUNCTION 'SCMS_BINARY_TO_XSTRING'
         EXPORTING
           input_length = lv_bin_length
         IMPORTING
           buffer       = lv_xstring
         TABLES
 *         binary_tab   = lt_raw_data.
           binary_tab   = it_binary.
     ENDIF.
 

    lo_attach_service->create_attachment(
       EXPORTING
         iv_name         = CONV string( ls_file )
         iv_content_hex  = lv_xstring
     ).
 
    "JCRAIG File Upload Change/MOD 20250507 end
 *  *  ************************************
 
    CALL FUNCTION '/SMPL/PPPI_FM_ATTCH_GET'
       EXPORTING
         im_order                      = im_order
        IM_MATNR                       = im_matnr
        IM_CHARG                       = im_charg
        IT_EXP_ATT                     = it_exp_att_made
      IMPORTING
        ET_FILE_LIST                   = lt_file_list
        ET_CREATED_BY                  = lt_created_by
        ET_CREATED_DATE                = lt_created_date
        ET_CREATED_TIME                = lt_created_time
        ET_STATUS                      = lt_status
      CHANGING
        CT_FILE_LIST                   = CT_FILE_LIST
        CT_CREATED_BY                  = CT_CREATED_BY
        CT_CREATED_DATE                = CT_CREATED_DATE
        CT_CREATED_TIME                = CT_CREATED_TIME
        CT_STATUS                      = CT_STATUS
      EXCEPTIONS
        INSPECTION_LOT_MISSING         = 1
        LOAD_ATTACHMENTS_ERROR         = 2
        GOS_UTIL_NOT_INITIALIZED       = 3
        OTHERS                         = 4
               .
 
    CASE sy-subrc.
       WHEN 0.
         "Success
       WHEN 1.
         RAISE inspection_lot_missing.
       WHEN 2.
         RAISE gos_util_not_initialized.
       WHEN 3.
         RAISE load_attachments_error.
       WHEN OTHERS.
         " Raise internal exception
     ENDCASE.
 

    CASE sy-subrc.
       WHEN 1.
         MESSAGE TEXT-002 TYPE lc_error RAISING gos_util_not_initialized.
       WHEN 2.
         MESSAGE TEXT-001 TYPE lc_error RAISING inspection_lot_missing.
       WHEN 3.
         MESSAGE TEXT-004 TYPE lc_error RAISING load_attachments_error.
     ENDCASE.
 
    DATA: lv_file_count TYPE i.
     DESCRIBE TABLE lt_file_list LINES lv_file_count.
     IF sy-subrc <> 0.
       MESSAGE TEXT-004 TYPE lc_error RAISING load_attachments_error.
     ENDIF.
 
    CLEAR ex_filename.
     lv_loop = 1.
     " MOD Start - Allow for expected attachment check JCRAIG
     IF ct_exp_att IS NOT INITIAL.
       LOOP AT ct_exp_att INTO DATA(ls_exp_att).
         " Find matching expected attachment row
         IF ct_file_list[ im_index ] IS INITIAL.
           " Update each of the individual output tables at the same index
           ct_file_list[ im_index ]    = lt_file_list[ lv_file_count ].
           ct_created_by[ im_index ]   = lt_created_by[ lv_file_count ].
           ct_created_date[ im_index ] = lt_created_date[ lv_file_count ].
           ct_created_time[ im_index ] = lt_created_time[ lv_file_count ].
           ct_status[ im_index ]       = lt_status[ lv_file_count ].
           "ct_exp_att remains the same
         ELSE.
           " error message for reupload handled earlier in FM
         ENDIF.
       ENDLOOP.
       " MOD End - Allow for expected attachment check JCRAIG
     ELSE.
       IF ct_file_list IS INITIAL.
         READ TABLE lt_file_list INTO DATA(lv_latest_file) INDEX lines( lt_file_list ).
         ex_filename = lv_latest_file.
       ELSEIF ct_file_list[ 1 ] IS NOT INITIAL. " entries exist in xstep
         " CLEANUP STEP: Remove accidental empty line due to add table row\
         LOOP AT ct_file_list ASSIGNING FIELD-SYMBOL(<fs_file>) FROM 1.
           IF <fs_file> IS INITIAL.
             DELETE ct_file_list INDEX sy-tabix.
             DELETE ct_created_by INDEX sy-tabix.
             DELETE ct_created_date INDEX sy-tabix.
             DELETE ct_created_time INDEX sy-tabix.
             DELETE ct_status INDEX sy-tabix.
             EXIT. " delete only one if needed
           ENDIF.
         ENDLOOP.
         "Append entries
         LOOP AT lt_file_list INTO ls_file_list.
           READ TABLE ct_file_list WITH TABLE KEY table_line = ls_file_list TRANSPORTING NO FIELDS.
           IF sy-subrc <> 0.
             APPEND lt_file_list[ lv_loop ] TO ct_file_list.
             APPEND lt_created_by[ lv_loop ] TO ct_created_by.
             APPEND lt_created_date[ lv_loop ] TO ct_created_date.
             APPEND lt_created_time[ lv_loop ] TO ct_created_time.
             APPEND lt_status[ lv_loop ] TO ct_status.
           ELSE.                                             "20250909
             " Basic design Fix - If uploading file that has been deleted previously
             IF lt_status[ sy-tabix ] <> ct_status[ sy-tabix ].  "comparing attached to deleted status
               " This is a re-upload of a deleted file - ADD as new entry, don't replace
               APPEND lt_file_list[ lv_loop ] TO ct_file_list.
               APPEND lt_created_by[ lv_loop ] TO ct_created_by.
               APPEND lt_created_date[ lv_loop ] TO ct_created_date.
               APPEND lt_created_time[ lv_loop ] TO ct_created_time.
               APPEND lt_status[ lv_loop ] TO ct_status.
             ENDIF.
             " If not a re-upload scenario, skip this entry (it's already there)
           ENDIF.
           lv_loop = lv_loop + 1.
         ENDLOOP.
       ELSE. "first entry
         CLEAR: ct_created_by, ct_created_date, ct_created_time, ct_file_list, ct_status. " ct_exp_att.
         ct_file_list    = lt_file_list.
         ct_created_by   = lt_created_by.
         ct_created_date  = lt_created_date.
         ct_created_time  = lt_created_time.
         ct_status   = lt_status.
       ENDIF.
     ENDIF.
 
    "Populate validation flag if needed after successful execution
     IF sy-subrc = 0.
       ex_val_flag = 1.
     ENDIF.
   ENDIF.
 ENDFUNCTION.
