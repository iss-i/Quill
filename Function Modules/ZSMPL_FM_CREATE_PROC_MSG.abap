FUNCTION ZSMPL_FM_CREATE_PROC_MSG.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(I_PLANT) TYPE  WERKS_D
 *"     REFERENCE(I_DATE) TYPE  DATE OPTIONAL
 *"     REFERENCE(I_TIME) TYPE  TIMS OPTIONAL
 *"     REFERENCE(I_MATNR) TYPE  MATNR
 *"     REFERENCE(I_GI_QTY) TYPE  ERFMG
 *"     REFERENCE(I_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(I_ERFME) TYPE  MEINS OPTIONAL
 *"     REFERENCE(I_BWART) TYPE  BWART OPTIONAL
 *"     REFERENCE(I_RSNUM) TYPE  RSNUM OPTIONAL
 *"     REFERENCE(I_RSPOS) TYPE  RSPOS OPTIONAL
 *"     REFERENCE(I_MSG_HEAD) TYPE  CO_SOURCE OPTIONAL
 *"     REFERENCE(I_BATCH) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(I_PHASE) TYPE  VORNR OPTIONAL
 *"     REFERENCE(I_STLOC) TYPE  LGORT_D
 *"     REFERENCE(I_FLAG) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(I_MATCH_FLAG) TYPE  CHAR1 OPTIONAL
 *"  EXCEPTIONS
 *"      MESSAGE_CREATION_FAIL
 *"      CHARACTERISTIC_ERROR
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_CREATE_PROC_MSG                               *
 * Created by      : Carolina Osorno (COSORNO)                              *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : October 05, 2018                                       *
 * Purpose         : Send process Message for Z_PICONS                      *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development         SEDK901153     COSORNO        10/05/2018     *
 *--------------------------------------------------------------------------*
 
  DATA: lt_process_header TYPE TABLE OF bapi_rcomhapi,
         lt_process_char   TYPE TABLE OF bapi_rcomeapi,
         lt_header_ret     TYPE TABLE OF bapi_rcomhrtc,
         lt_char_ret       TYPE TABLE OF bapi_rcomertc,
         lt_return         TYPE TABLE OF bapiret2,
         ls_process_header TYPE bapi_rcomhapi,
         ls_process_char   TYPE bapi_rcomeapi,
         ls_header_ret     TYPE bapi_rcomhrtc,
         ls_char_ret       TYPE bapi_rcomertc,
         ls_return         TYPE bapiret2,
         lv_message_id     TYPE co_msid2,
         lv_time           TYPE sy-uzeit,
         lv_date           TYPE sy-datum,
         lv_matnr          TYPE matnr,
         lv_batch          TYPE charg_d.
 
  CONSTANTS: lc_na1 TYPE char3 VALUE 'N/A',
              lc_na2 TYPE char3 VALUE 'NA'.
 
  IF i_flag IS NOT INITIAL.
     IF i_match_flag IS NOT INITIAL AND i_flag = i_match_flag.
       "Continue
     ELSE.
       RETURN.
     ENDIF.
   ENDIF.
 
  lv_matnr = i_matnr.
   lv_batch = i_batch.
 
  CONDENSE: lv_matnr, lv_batch.
   TRANSLATE lv_matnr TO UPPER CASE.
   TRANSLATE lv_batch TO UPPER CASE.
 
  "Don't create process message if values contain N/A
   IF ( lv_matnr = lc_na1 OR lv_matnr = lc_na2 ) OR ( lv_batch = lc_na1 OR lv_batch = lc_na2 ) OR i_matnr IS INITIAL.
     RETURN.
   ENDIF.
 
   "If date is null, set it to the current date
   IF i_date IS INITIAL.
     lv_date = sy-datum.
   ELSE.
     lv_date = i_date.
   ENDIF.
   "If time is null, set it to the current time
   IF i_time IS INITIAL.
     lv_time = sy-uzeit.
   ELSE.
     lv_time = i_time.
   ENDIF.
 
  "Header
   ls_process_header-proc_mess_id_tmp = ls_process_header-proc_mess_id_tmp + 1.
   lv_message_id = ls_process_header-proc_mess_id_tmp.
   ls_process_header-plant = i_plant.
   ls_process_header-proc_mess_category = 'Z_PICONS'.
 
  IF i_msg_head IS INITIAL.
     ls_process_header-sender_name = sy-uname.
   ELSE.
     ls_process_header-sender_name = i_msg_head.
   ENDIF.
 
  "Characteristics
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_EVENT_DATE'.
   ls_process_char-data_type = 'DATE'.
   ls_process_char-char_value = lv_date.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_EVENT_TIME'.
   ls_process_char-data_type = 'TIME'.
   ls_process_char-char_value = lv_time.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_MATERIAL'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_matnr.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_MATERIAL_CONSUMED'.
   ls_process_char-data_type = 'NUM'.
   WRITE i_gi_qty to ls_process_char-char_value.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_PROCESS_ORDER'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_order.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_UNIT_OF_MEASURE'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_erfme.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'ZSMPL_CHAR_MOVEMENT_TYPE'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_bwart.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_RESERVATION_ITEM'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_rspos.
   APPEND ls_process_char TO lt_process_char.
 

  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_RESERVATION'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_rsnum.
   APPEND ls_process_char TO lt_process_char.
 
  "KWVP774
   CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_BATCH'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_batch.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_PHASE'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_phase.
   APPEND ls_process_char TO lt_process_char.
 
  CLEAR  ls_process_char.
   ls_process_char-proc_mess_id_tmp = lv_message_id.
   ls_process_char-name_char = 'PPPI_STORAGE_LOCATION'.
   ls_process_char-data_type = 'CHAR'.
   ls_process_char-char_value = i_stloc.
   APPEND ls_process_char TO lt_process_char.
   "KWVP774
 

  "Append message header
   APPEND ls_process_header TO lt_process_header.
 

  "Create Message
   CALL FUNCTION 'BAPI_PROCESS_MESSAGE_CREATEMLT'
     TABLES
       procmessheader       = lt_process_header
       procmesscharac       = lt_process_char
 *     PROCMESSTEXTLINES    =
 *     PROCESSMESSAGENEW    =
       procmessheaderreturn = lt_header_ret
       procmesscharacreturn = lt_char_ret
       return               = lt_return.
 
  "Characteristic Erros
   LOOP AT lt_char_ret INTO ls_char_ret.
     IF ls_char_ret-type = 'E'.
       RAISE characteristic_error.
     ENDIF.
   ENDLOOP.
 
  "Header Errors
   LOOP AT lt_header_ret INTO ls_header_ret.
     IF ls_header_ret-type = 'E'.
       RAISE message_creation_fail.
     ENDIF.
   ENDLOOP.
 
  "General Errors
   LOOP AT lt_return INTO ls_return.
     IF ls_return-type = 'E'.
       RAISE message_creation_fail.
     ENDIF.
   ENDLOOP.
 
*  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
 *  EXPORTING wait = 'X'.
 


ENDFUNCTION.
