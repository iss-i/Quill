FUNCTION ZSMPL_FM_OUTPUT_BATCH_SIZE.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_DEF_PL_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_PL_QTY) TYPE  ERFMG OPTIONAL
 *"     REFERENCE(IV_ACT_QTY) TYPE  ERFMG OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_PO_QTY) TYPE  ERFMG
 *"     REFERENCE(EV_RATIO) TYPE  ERFMG
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_OUTPUT_BATCH_SIZE                       *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Calculate updated batch size based on planned qty  *
 *                   and existing qty - also pass reduction ratio to be *
 *                   passed for further required qty calculations       *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
DATA: lv_string TYPE string,
         lv_value TYPE string,
         ls_prepare_msg_frontend TYPE /SMPL/EBR_PREP_MSG_FRONTEND.
 
DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
 
  "Calculate new batch size
   ev_po_qty = iv_pl_qty - iv_act_qty.
 
  " Display warning that batch size calculation cannot be negative (EBR)
   IF ev_po_qty < 0.
     ev_po_qty = 0.
     lv_string = 'Calculation error - Batch Size cannot be negative'.
 
    IF lcl_websocket->gv_function = 'SMPL_EBR' AND lv_string IS NOT INITIAL.
       ls_prepare_msg_frontend-message_custom = abap_true.
       ls_prepare_msg_frontend-message_source = '2'.
       ls_prepare_msg_frontend-message_type = 'W'.
       ls_prepare_msg_frontend-message_text = lv_string.
       CALL METHOD /smpl/ebr_cl_web_sock_hndl=>prepare_message_for_frontend
         EXPORTING
           is_prepare_message = ls_prepare_msg_frontend.
     ELSE.
         " Display warning that batch size calculation cannot be negative (GUI)
       MESSAGE 'Calculation error - Batch Size cannot be negative' TYPE 'S' DISPLAY LIKE 'W'.
     ENDIF.
 
  ENDIF.
 
  " pass reduction ratio
   IF iv_act_qty IS NOT INITIAL.
     IF iv_pl_qty = iv_def_pl_qty AND iv_def_pl_qty IS NOT INITIAL.
       ev_ratio = ev_po_qty / iv_pl_qty.  "iv_act_qty / iv_pl_qty.
     ELSE.
       "If planned quantity has changed then adjust conversion ratio based on original
       ev_ratio = ev_po_qty / iv_def_pl_qty.
     ENDIF.
   ELSE.
     ev_ratio = 1.
   ENDIF.
 

ENDFUNCTION.
