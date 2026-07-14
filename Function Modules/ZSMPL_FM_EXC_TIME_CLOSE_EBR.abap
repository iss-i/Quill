FUNCTION zsmpl_fm_exc_time_close_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_AUFNR) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_TIMER) TYPE  CHAR30 OPTIONAL
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  zsmpl_pppi_exc_time_close                                          *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Kills hourglass timer process or tells EBR to close the       *
 *       timer popup inside the application                            *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
 
  DATA: lv_command TYPE string,
         lv_params  TYPE string.
 
  DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).   "zcl_smpl_ebr_apc_ws( ).
   DATA: lo_socket TYPE REF TO /smpl/ebr_cl_web_sock_hndl,  "zcl_smpl_ebr_web_socket_handle,
         lv_string TYPE string.
 
  CREATE OBJECT lo_socket.
   " To suppress the comment pop-up for Simple EBR and ask the front end to launch the pop-up
   IF lcl_websocket->gv_function NE gc_smpl_ebr.
 
    " Kill Hourglass.exe process
     lv_command = 'taskkill'.
     lv_params = '/f /t /im Hourglass.exe'.
 
    CALL METHOD cl_gui_frontend_services=>execute
       EXPORTING
         application = lv_command
         parameter   = lv_params
         minimized   = 'X'.
 
  ELSE.
 
    CONCATENATE '<input name="excursionTimer" value="stop_timer"><input name="timer" value="' iv_timer '">' INTO lv_string.
     lo_socket->send_message( i_application_id = gc_smpl_ebr_amc_mc   "+PAM
                              i_channel_id     = '/ui5'
                              i_string         = lv_string
                              i_unique_id      = lcl_websocket->gv_unique_id ).
 
  ENDIF.
 
ENDFUNCTION.
