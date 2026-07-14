FUNCTION zsmpl_fm_scan_barcode_ebr .
 *"--------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(LEN0) TYPE  I OPTIONAL
 *"     REFERENCE(LEN1) TYPE  I OPTIONAL
 *"     REFERENCE(LEN2) TYPE  I OPTIONAL
 *"     REFERENCE(LEN3) TYPE  I OPTIONAL
 *"     REFERENCE(LEN4) TYPE  I OPTIONAL
 *"     REFERENCE(LEN5) TYPE  I OPTIONAL
 *"     REFERENCE(LEN6) TYPE  I OPTIONAL
 *"     REFERENCE(LEN7) TYPE  I OPTIONAL
 *"     REFERENCE(LEN8) TYPE  I OPTIONAL
 *"     REFERENCE(LEN9) TYPE  I OPTIONAL
 *"     REFERENCE(IV_TITLE) TYPE  CHAR100 OPTIONAL
 *"     REFERENCE(IV_TEXT1) TYPE  CHAR100 OPTIONAL
 *"     REFERENCE(IV_TEXT2) TYPE  CHAR100 OPTIONAL
 *"     REFERENCE(IV_TEXT3) TYPE  CHAR100 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_VALUE) TYPE  CHAR100
 *"     REFERENCE(STR0) TYPE  CHAR30
 *"     REFERENCE(STR1) TYPE  CHAR30
 *"     REFERENCE(STR2) TYPE  CHAR30
 *"     REFERENCE(STR3) TYPE  CHAR30
 *"     REFERENCE(STR4) TYPE  CHAR30
 *"     REFERENCE(STR5) TYPE  CHAR30
 *"     REFERENCE(STR6) TYPE  CHAR30
 *"     REFERENCE(STR7) TYPE  CHAR30
 *"     REFERENCE(STR8) TYPE  CHAR30
 *"     REFERENCE(STR9) TYPE  CHAR30
 *"--------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  ZSMPL_FM_SCAN_BARCODE                                            *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Scan value in popup and break it up into different values     *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   CONSTANTS lc_smpl_ebr TYPE string VALUE 'SMPL_EBR' ##NO_TEXT.
   CONSTANTS lc_smpl_ebr_amc_mc TYPE amc_application_id VALUE '/SMPL/EBR_AMC_MC' ##NO_TEXT.
 
  DATA: lt_lengths    TYPE TABLE OF i,
         lt_substrings TYPE TABLE OF string,
         lv_substring  TYPE string,
         lv_offset     TYPE i,
         lv_len        TYPE i,
         lv_value      TYPE meth_txt,
         lv_answer     TYPE answer.
 
  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ). "zcl_smpl_ebr_apc_ws( ).
   DATA:  lo_socket    TYPE REF TO /smpl/ebr_cl_web_sock_hndl. "zcl_smpl_ebr_web_socket_handle.
 
  CREATE OBJECT lo_socket.
   " To suppress the comment pop-up for Simple EBR and ask the front end to launch the pop-up
   IF lcl_websocket->gv_function = lc_smpl_ebr.
     lv_value = ev_value = lcl_websocket->gv_scantext.
     IF ev_value IS INITIAL.
       CONCATENATE '<input name="showscanpopup" value="show_scan_popup_dialog">'
       '<input name="scantext" value="' iv_text1 '">' lcl_websocket->gv_request_string INTO DATA(lv_string).
       lo_socket->send_message( i_string  = lv_string
                                i_unique_id = lcl_websocket->gv_unique_id ).
       RETURN.
     ENDIF.
 
  ELSE.
 
    CALL FUNCTION 'POPUP_TO_MODIFY_TEXT'
       EXPORTING
         textline1      = iv_text1
         textline2      = iv_text2
         textline3      = iv_text3
         titel          = iv_title
         value1         = ''
       IMPORTING
         answer         = lv_answer
         value1         = lv_value
       EXCEPTIONS
         titel_too_long = 1
         OTHERS         = 2.
     IF sy-subrc EQ 0.
       IF lv_answer NE 'J'.
         EXIT.
       ENDIF.
     ENDIF.
   ENDIF.
   APPEND len0 TO lt_lengths.
   APPEND len1 TO lt_lengths.
   APPEND len2 TO lt_lengths.
   APPEND len3 TO lt_lengths.
   APPEND len4 TO lt_lengths.
   APPEND len5 TO lt_lengths.
   APPEND len6 TO lt_lengths.
   APPEND len7 TO lt_lengths.
   APPEND len8 TO lt_lengths.
   APPEND len9 TO lt_lengths.
 
  lv_len = len0 + len1 + len2 + len3 + len4 + len5 + len6 + len7 + len8 + len9.
   IF  strlen( lv_value ) EQ lv_len.
     CLEAR: lv_len.
   ELSE.
     IF  lcl_websocket->gv_function = lc_smpl_ebr.
       DATA: ls_prepare_msg_frontend TYPE /smpl/ebr_prep_msg_frontend. "zst_prepare_msg_frontend.
       ls_prepare_msg_frontend-message_custom = abap_true.
       ls_prepare_msg_frontend-message_source = ' '.
       ls_prepare_msg_frontend-message_type = 'E'.
       ls_prepare_msg_frontend-message_text = 'String is not long enough: Please change the offset length or string'.
       CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
         EXPORTING
           is_prepare_message = ls_prepare_msg_frontend.
 *      lv_string = '<input name="error" value="display_error"><input name="error" value="String is not long enough: Please change the offset length or string">'.
 *      lo_socket->send_message( i_application_id = lc_smpl_ebr_amc_mc
 *                          i_channel_id     = '/ui5'
 *                          i_string         = lv_string
 *                          i_unique_id      = lcl_websocket->gv_unique_id ).
       CLEAR: lcl_websocket->gv_scantext.
       RETURN.
     ELSE.
 
      MESSAGE 'String is not long enough: Please change the offset length or string'(001) TYPE 'E'.
     ENDIF.
     EXIT.
   ENDIF.
 
  lv_offset = 0.
 
  LOOP AT lt_lengths INTO lv_len.
     IF lv_offset < strlen( lv_value ).
       lv_substring = lv_value+lv_offset(lv_len).
     ELSE.
       lv_substring = ''.
     ENDIF.
     APPEND lv_substring TO lt_substrings.
     ADD lv_len TO lv_offset.
   ENDLOOP.
 
  LOOP AT lt_substrings INTO lv_substring.
     CASE sy-tabix.
       WHEN 1.
         str0   = lv_substring.
       WHEN 2.
         str1  = lv_substring.
       WHEN 3.
         str2   = lv_substring.
       WHEN 4.
         str3   = lv_substring.
       WHEN 5.
         str4   = lv_substring.
       WHEN 6.
         str5   = lv_substring.
       WHEN 7.
         str6   = lv_substring.
       WHEN 8.
         str7   = lv_substring.
       WHEN 9.
         str8   = lv_substring.
       WHEN OTHERS.
         str9   = lv_substring.
     ENDCASE.
   ENDLOOP.
 
  CLEAR:lcl_websocket->gv_scantext.
 
ENDFUNCTION.
