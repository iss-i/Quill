FUNCTION zsmpl_fm_exc_time_reopen_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_WERKS) TYPE  WERKS_D OPTIONAL
 *"     REFERENCE(IV_AUFNR) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_TIMER) TYPE  CHAR30 OPTIONAL
 *"     REFERENCE(IV_END_DATE) TYPE  DATS
 *"     REFERENCE(IV_END_TIME) TYPE  TIMS
 *"  EXCEPTIONS
 *"      HOURGLASS_NOT_CONFIGURED
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  zsmpl_fm_exc_time_reopen                                         *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *        Close and open a timer without restarting it                 *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
 
  DATA lv_time_limit TYPE int4.
 
  DATA:  lo_socket    TYPE REF TO /smpl/ebr_cl_web_sock_hndl.  "zcl_smpl_ebr_web_socket_handle.
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).   "zcl_smpl_ebr_apc_ws( ).
 
  CREATE OBJECT lo_socket.
 
  IF lcl_websocket->gv_function EQ gc_smpl_ebr.
 
    CONCATENATE '<input name="excursionTimer" value="start_timer"><input name="plant" value="' iv_werks '">'
                '<input name="timer" value="' iv_timer '">'
                '<input name="PO" value="' iv_aufnr '">'
                '<input name="end_date" value="' iv_end_date '">'
                '<input name="end_time" value="' iv_end_time '">'
                INTO DATA(lv_string).
     lo_socket->send_message( i_application_id = gc_smpl_ebr_amc_mc   "+PAM
                              i_channel_id     = '/ui5'
                              i_string         = lv_string
                              i_unique_id      = lcl_websocket->gv_unique_id ).
   ELSE.
 
    CALL FUNCTION 'ZSMPL_FM_EXC_TIME_CLOSE_EBR'
       EXPORTING
         iv_aufnr = iv_aufnr
         iv_timer = iv_timer.   "20250909 addition
 
    WAIT UP TO 1 SECONDS.
 
    CALL FUNCTION '/SMPL/PPPI_FM_EXC_TIME_OPN'
       EXPORTING
         iv_werks                 = iv_werks
         iv_aufnr                 = iv_aufnr
 *       iv_timer                 = iv_timer
         iv_end_date              = iv_end_date
         iv_end_time              = iv_end_time
       EXCEPTIONS
         hourglass_not_configured = 1.
 
    IF sy-subrc NE 0.
       RAISE hourglass_not_configured.
     ENDIF.
 
  ENDIF.
 



ENDFUNCTION.
