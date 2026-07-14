FUNCTION zsmpl_fm_exc_time_continue_ebr.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_WERKS) TYPE  WERKS_D
 *"     REFERENCE(IV_AUFNR) TYPE  AUFNR
 *"     REFERENCE(IV_TIMER) TYPE  CHAR30 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_START_TIME) TYPE  TIMS
 *"     REFERENCE(EV_START_DATE) TYPE  DATS
 *"     REFERENCE(EV_END_TIME) TYPE  TIMS
 *"     REFERENCE(EV_END_DATE) TYPE  DATS
 *"  EXCEPTIONS
 *"      TIMER_NOT_STARTED
 *"      HOURGLASS_NOT_CONFIGURED
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  zsmpl_fm_exc_time_continue                                       *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Reopen an existing timer but do not restart it                *
 *          - Raise an exception if not timer found for the  order     *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
 
  " Check if data exists to be loaded
   SELECT SINGLE * FROM /smpl/pppi_extim
     WHERE plant = @iv_werks
       AND aufnr = @iv_aufnr
       AND timer = @iv_timer
      INTO @DATA(ls_exc_time).
 
  IF sy-subrc NE 0.
     MESSAGE 'No dispense timer started for the current order'(002) TYPE gc_type_e raising TIMER_NOT_STARTED.
   ENDIF.
 
  CALL FUNCTION 'ZSMPL_FM_EXC_TIME_REOPEN_EBR'
     EXPORTING
       iv_aufnr = iv_aufnr
       iv_werks = iv_werks
       iv_timer = iv_timer
       iv_end_time = ls_exc_time-end_time
       iv_end_date = ls_exc_time-end_date
     EXCEPTIONS
       hourglass_not_configured = 1.
 
  IF sy-subrc NE 0.
     RAISE hourglass_not_configured.
   ENDIF.
 
  " Return time data for current timer
   ev_start_time = ls_exc_time-start_time.
   ev_start_date = ls_exc_time-start_date.
   ev_end_time = ls_exc_time-end_time.
   ev_end_date = ls_exc_time-end_date.
 

ENDFUNCTION.
