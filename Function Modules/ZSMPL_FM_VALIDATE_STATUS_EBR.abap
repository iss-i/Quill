FUNCTION zsmpl_fm_validate_status_ebr.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_EQUIPMENT) TYPE  EQUNR
 *"     REFERENCE(IV_EQUI_STAT) TYPE  EQFNR
 *"     REFERENCE(IV_BYPASS) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IV_CALIB_DUE_DATE) TYPE  DATS OPTIONAL
 *"     REFERENCE(IV_MULTI_PO) TYPE  ABAP_BOOL OPTIONAL
 *"  EXCEPTIONS
 *"      EQUIPMENT_STATUS_INCORRECT
 *"      CALIBRATION_DUE_DATE_INCORRECT
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_VALIDATE_STATUS_EBR                       *
 * Project/Ticket  : SMPL                                               *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : JCRAIG Jason Craig                                 *
 * Functional                                                           *
 *    Analyst:     : FVDMERWE Frieda van der Merwe                      *
 * Create Date     : 21.11.2025                                         *
 * Description     : Equipment Logbooks ~ Validate equipment status and *
 *                   perform clean and PharmaTool check                 *
 *                                                                      *
 *----------------------------------------------------------------------*
 *-------------------------MODIFICATION LOG-----------------------------*
 *  MOD1 - Add validation to check if line clearance is complete        *                                                 *
 *  MOD2 - Add STANDARDIZATION_CHECK for new standardization            *
 *         variant XStep                                                *
 *  MOD3 - Add Calibration Due Date from equipment characteristics      *                                          *
 *  MOD4 - Allow multi-order assignment                                 *
 *----------------------------------------------------------------------*
 
  "Data declaration
   CONSTANTS: lc_icon_warn TYPE iconname VALUE 'ICON_MESSAGE_WARNING',
              lc_warn_txt  TYPE sta_text VALUE 'WARNING'.
 
  DATA: l_response   TYPE char30,
         l_status_upd TYPE /smpl/str_de_stat_class,
         l_id         TYPE icon-id.
 
  "EBR Start
   DATA: lv_string TYPE string.
   DATA: ls_prepare_msg_frontend TYPE /smpl/ebr_prep_msg_frontend. "Message review changes
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
   DATA:  lo_socket    TYPE REF TO /smpl/ebr_cl_web_sock_hndl.
 
  CREATE OBJECT lo_socket.
   "EBR End
 
  "If the bypass flag is equal to 1 the validation needs to be performed else exit.
   IF iv_bypass EQ '0' AND iv_bypass IS NOT INITIAL.
     EXIT.
     " If bypass flag is equal to 2 then line clearance is not completed - MOD1 Start
   ELSEIF iv_bypass EQ '2' AND iv_bypass IS NOT INITIAL.
     MESSAGE TEXT-009 TYPE 'S' DISPLAY LIKE 'E'.
     RAISE equipment_status_incorrect.
     "MOD1 End
   ENDIF.
 
  PERFORM equipment_cleaning_rules USING iv_equi_stat l_response l_status_upd.
 
  IF l_response IS NOT INITIAL.
 
    "MOD4 Start
     IF iv_multi_po = abap_true AND l_response = TEXT-004.
       "Continue with a warning that equipment is assigned in another order
       IF lcl_websocket->gv_function = 'SMPL_EBR'.
         lv_string = TEXT-004 && ` ` && '-' && ` ` && iv_equipment.
 
*message Review Changes
         ls_prepare_msg_frontend-message_custom = abap_true.
         ls_prepare_msg_frontend-message_source = '2'.
         ls_prepare_msg_frontend-message_type = 'W'.
 *    ls_prepare_msg_frontend-message_text = lcl_websocket->gv_request_string.
         ls_prepare_msg_frontend-message_text = lv_string.
         CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
           EXPORTING
             is_prepare_message = ls_prepare_msg_frontend.
       ELSE.
         MESSAGE TEXT-004 && ` ` && '-' && ` ` && iv_equipment TYPE 'S' DISPLAY LIKE 'W'.
       ENDIF.
     ELSE.
       "MOD4 End
 
      "Raise exception if equipment is not updateable
       MESSAGE TEXT-004 TYPE 'S' DISPLAY LIKE 'E'.
       RAISE equipment_status_incorrect.
     ENDIF.  "MOD4
   ENDIF.
 
  "MOD2 Start - STANDARDIZATION_CHECK addition
   SELECT SINGLE id "They table key is an icon and i have no way to call against the icon itself
     FROM icon
     INTO l_id
     WHERE name = lc_icon_warn.
 
  DATA: l_equnr TYPE equnr,
         l_error TYPE boolean.
 
  l_equnr = iv_equipment.
 
  PERFORM standardization_check USING l_equnr l_error.
   "If equipment has not been standardized, inform operator
   IF l_error EQ 'S'.
 
    CALL FUNCTION 'POPUP_TO_INFORM'
       EXPORTING
         titel = lc_warn_txt
         txt1  = l_id
         txt2  = TEXT-016.
   ENDIF.
   "MOD2 End
 
  "MOD3 Start
   DATA: l_today TYPE dats.
 
  l_today = sy-datum.
 
  IF iv_calib_due_date IS NOT INITIAL
     AND iv_calib_due_date NE '0'.
 
    IF iv_calib_due_date LT l_today.
       MESSAGE TEXT-022 TYPE 'S' DISPLAY LIKE 'E'.
       RAISE calibration_due_date_incorrect.
     ENDIF.
 
  ENDIF.
   "MOD3 End
 
ENDFUNCTION.
 
FORM equipment_cleaning_rules USING lv_status lv_response lv_status_upd.
 
  "Equipment cleaning engine
   SELECT SINGLE * FROM /smpl/elb_eqstat
     WHERE eq_stat = @lv_status INTO @DATA(ls_status_details).
 
  CASE ls_status_details-class(1).
     WHEN 'U'. "U -> Use
       lv_response = TEXT-004.
     WHEN 'C'. "C -> Cleaned
       "Continue
       lv_status_upd = 'U1'.
     WHEN 'P'. "P -> Pending
       lv_response = TEXT-005.
 
      "MOD1 Start - STANDARDIZATION_REQUIRED addition
     WHEN 'S'. "S -> Standardized
       "Continue
       lv_status_upd = 'U1'.
     WHEN 'G1'. "G1 -> Standardization Required
       lv_response = TEXT-016.
       "MOD1 End
 
      "MOD2 Start - Multi-PO Assignment
     WHEN 'M'. "M -> Multiple Order Equipment Assignment
       "Continue
       lv_status_upd = 'U2'.
       "MOD2 End
 
    WHEN OTHERS. "Includes I -> Intermediate, G -> General
       lv_response = TEXT-006.
   ENDCASE.
 
ENDFORM.
