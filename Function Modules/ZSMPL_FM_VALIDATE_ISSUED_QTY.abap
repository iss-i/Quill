FUNCTION zsmpl_fm_validate_issued_qty.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_CURRENT_QTY) TYPE  ERFMG
 *"     REFERENCE(IV_DEFAULT_QTY) TYPE  ERFMG
 *"     REFERENCE(IV_PREVIOUS_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_REQ_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_PCT) TYPE  INT1 OPTIONAL
 *"     REFERENCE(IV_ISS_DIFF) TYPE  ABAP_BOOL OPTIONAL
 *"     REFERENCE(IV_ADD_ISS) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_DEVI_UPDOWN) TYPE  FLAG OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_ISS_DIFF) TYPE  ERFMG
 *"  EXCEPTIONS
 *"      ISSUED_QUANTITY_CHANGED
 *"      QUANTITY_OUT_OF_TOLERANCE
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_VALIDATE_ISSUED_QTY                       *
 * Project/Ticket  : AZGA                                               *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : GGROTIUS Gustav Grotius                            *
 * Functional                                                           *
 *    Analyst:     : <SAP ID> <Full Name>                               *
 * Create Date     : 11.08.2025                                         *
 * Description     : Validate the Issued Qty when a user manually       *
 *                   changes it in the XStep. This is execute on input  *
 *                   validation on the Issued Qty                       *
 *                   Additionally, validate the issued quantity against *
 *                   provided tolerance ranges such as 1% validation    *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *   MOD001 KWVP774  Add EBR compatibility & issued difference calculation *
 *----------------------------------------------------------------------*
 
  DATA: lv_pct TYPE erfmg,
         lv_min TYPE erfmg,
         lv_max TYPE erfmg.
 
  DATA: lv_string TYPE string,
         ls_prepare_msg_frontend TYPE /SMPL/EBR_PREP_MSG_FRONTEND, "Message review changes
         lv_diff TYPE erfmg,
         lv_pct_char  TYPE char3,
         lv_current_qty TYPE erfmg.
 
  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
  "Write percentage value to 3 decimal value & char variable
   lv_pct = iv_pct.
   lv_pct_char = iv_pct.
 
  "Get Tolerance range based on import percentage
   lv_max = iv_req_qty + ( iv_req_qty * ( lv_pct / 100 ) ).
   lv_min = iv_req_qty - ( iv_req_qty * ( lv_pct / 100 ) ).
 
    "8/04 KVWP774 Addition
   "Calculate difference in issued qty in case additional amount is weighed out
   " to ensure consumption is accurate
   IF iv_iss_diff = abap_true.
     lv_diff = iv_current_qty - iv_default_qty.
     IF lv_diff < 0.
       ev_iss_diff = 0.
     ELSE.
       ev_iss_diff = lv_diff.
     ENDIF.
   ENDIF.
 
  " Calculate issuing qty for additional issue table to be used for tolerance range validation
   IF iv_add_iss IS NOT INITIAL.
     lv_current_qty = iv_current_qty + iv_add_iss.
     IF iv_previous_qty > 0.
       lv_current_qty = lv_current_qty - iv_previous_qty.
     ENDIF.
   ELSE.
     lv_current_qty = iv_current_qty.
   ENDIF.
   "8/04 KVWP774 End
 
  "KWVP774 1/04
   " Raise EBR Compatible warning message for negative values
   IF lv_current_qty < iv_default_qty.
     lv_string = 'Issuing Quantity can not be less then previously issued quantity (negative value) - Issued Quantity will be zero'.
 
    IF lcl_websocket->gv_function = 'SMPL_EBR' AND lv_string IS NOT INITIAL.
       ls_prepare_msg_frontend-message_custom = abap_true.
       ls_prepare_msg_frontend-message_source = '2'.
       ls_prepare_msg_frontend-message_type = 'W'.
       ls_prepare_msg_frontend-message_text = lv_string.
       CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
         EXPORTING
           is_prepare_message = ls_prepare_msg_frontend.
     ENDIF.
   ENDIF.
 
  "KWVP774 8/04
   " Raise EBR Compatible warning message for issued qty's below the tolerance range
   IF lv_current_qty IS NOT INITIAL AND iv_pct IS NOT INITIAL.
     IF lv_min <= lv_current_qty AND lv_current_qty <= lv_max.
       "within range
     " Two scenarios: 1 - either display a warning for under tolerance, and raise a deviation for over tolerance
     " Or, 2 - raise a deviation  for over/under tolerance (iv_devi_updown = TRUE)
     ELSEIF lv_current_qty < lv_min AND iv_devi_updown IS INITIAL.
       CONCATENATE 'Quantity is below the allowed tolerance (' lv_pct_char '%)' INTO lv_string.
       IF lcl_websocket->gv_function = 'SMPL_EBR'.
         ls_prepare_msg_frontend-message_custom = abap_true.
         ls_prepare_msg_frontend-message_source = '2'.
         ls_prepare_msg_frontend-message_type = 'W'.
         ls_prepare_msg_frontend-message_text = lv_string.
         CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
           EXPORTING
             is_prepare_message = ls_prepare_msg_frontend.
        ELSE.
          MESSAGE 'Quantity is not within the allowed tolerance (' && iv_pct && '%)' TYPE 'S' DISPLAY LIKE 'W'.
        ENDIF.
     ELSE.
       "Raise deviation when issues qty's are above tolerance range
       MESSAGE 'Quantity is not within the allowed tolerance (' && iv_pct && '%)' TYPE 'S' DISPLAY LIKE 'E'.
       RAISE QUANTITY_OUT_OF_TOLERANCE.
     ENDIF.
   ENDIF.
 
*----------------------------------------------------------------------*
 *If the current value is 0:
 * - Either the W&D system is down
 * - This is GPF North where manual weighing is done
 * - Weighing for this item has not bee done yet
 *In all of these scenarios, skip the validation
 *----------------------------------------------------------------------*
   IF lv_current_qty = 0.
     RETURN.
 
*----------------------------------------------------------------------*
 *If the current value IS NOT 0, and the retrieved default IS NOT 0,
 * and the current and retrieved default do not match, it is GPF where
 * the W&D retrieved a quantity, but the user manually updated it in the
 * XStep. Trigger a deviation
 *----------------------------------------------------------------------*
   ELSEIF lv_current_qty NE 0
          AND iv_default_qty NE 0
          AND iv_current_qty NE iv_default_qty.
     RAISE issued_quantity_changed.
 
  ENDIF.
 
ENDFUNCTION.
